from __future__ import annotations

import uuid
from datetime import datetime

from src.application.interfaces.i_unit_of_work import IUnitOfWork
from src.domain.entities.booking import Booking, BookingStatus
from src.domain.entities.user import User
from src.domain.exceptions.domain_exceptions import (
    AssetNotBookableError,
    BookingNotCancellableError,
    EntityNotFoundError,
    InvalidBookingWindowError,
    SlotOverlapError,
)


class BookingService:
    """
    Concurrency strategy for resource booking is DIFFERENT from asset
    allocation, deliberately:

    Allocation uses pessimistic row locks (SELECT ... FOR UPDATE) because
    there's exactly one row (the asset) to serialize on, and lock hold time
    is short and simple.

    Booking overlap-checking is NOT done with a lock on the asset row,
    because that would serialize ALL booking attempts for a resource
    (even ones for entirely different days) behind a single lock — bad for
    throughput on a popular room. Instead we let Postgres's
    `EXCLUDE USING gist (asset_id WITH =, time_range WITH &&)` constraint
    (see migration 0003) do the real enforcement atomically at INSERT time,
    and use an application-level pre-check purely to produce a friendly,
    specific error message before we even try. This is the same
    "pre-check for UX + DB constraint for correctness" pattern already used
    for duplicate serial numbers in AssetService — see `_is_exclusion_violation`.

    No SELECT ... FOR UPDATE, no retry loop, no elevated isolation level are
    needed: the exclusion constraint makes the INSERT itself atomic with
    respect to the overlap check, so there is no window in which two
    concurrent transactions can both believe a slot is free.
    """

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def book_resource(
        self,
        *,
        acting_user: User,
        asset_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime,
        department_id: uuid.UUID | None,
        purpose: str | None,
    ) -> Booking:
        if end_time <= start_time:
            raise InvalidBookingWindowError("end_time must be after start_time.")
        if start_time < datetime.now(start_time.tzinfo):
            raise InvalidBookingWindowError("Cannot book a slot that starts in the past.")

        async with self._uow as uow:
            asset = await uow.assets.get_by_id(asset_id)  # plain read — no lock needed for this check
            if asset is None:
                raise EntityNotFoundError("Asset", str(asset_id))
            if not asset.is_bookable:
                raise AssetNotBookableError(str(asset_id))

            # Step 1: friendly pre-check. Cheap, index-backed (ix_bookings_asset_id
            # + ix_bookings_status), and lets us return a specific "overlaps
            # with 9:00-10:00" message. Provides no concurrency guarantee.
            conflicts = await uow.bookings.find_overlapping(asset_id, start_time, end_time)
            if conflicts:
                raise SlotOverlapError(str(asset_id))

            booking = Booking(
                id=uuid.uuid4(),
                asset_id=asset_id,
                booked_by_user_id=acting_user.id,
                department_id=department_id,
                start_time=start_time,
                end_time=end_time,
                status=BookingStatus.UPCOMING,
                purpose=purpose,
            )

            try:
                # Step 2: the INSERT. If a second transaction committed a
                # genuinely overlapping booking between our pre-check above
                # and this flush — the actual race window — Postgres raises
                # an exclusion-violation here rather than letting it commit.
                created = await uow.bookings.create_booking(booking)
            except Exception as exc:
                if _is_exclusion_violation(exc, "no_overlapping_bookings"):
                    raise SlotOverlapError(str(asset_id)) from exc
                raise

            await uow.commit()
            return created

    async def cancel_booking(self, *, acting_user: User, booking_id: uuid.UUID) -> None:
        async with self._uow as uow:
            booking = await uow.bookings.get_by_id(booking_id)
            if booking is None:
                raise EntityNotFoundError("Booking", str(booking_id))
            if booking.status not in (BookingStatus.UPCOMING, BookingStatus.ONGOING):
                raise BookingNotCancellableError(str(booking_id))

            await uow.bookings.cancel(booking_id)
            await uow.commit()

    async def get_booking(self, booking_id: uuid.UUID) -> Booking | None:
        async with self._uow as uow:
            return await uow.bookings.get_by_id(booking_id)

    async def get_calendar_for_asset(
        self, asset_id: uuid.UUID, from_time: datetime | None = None, to_time: datetime | None = None
    ) -> list[Booking]:
        async with self._uow as uow:
            return await uow.bookings.get_for_asset(asset_id, from_time, to_time)


def _is_exclusion_violation(exc: Exception, constraint_hint: str) -> bool:
    """
    Best-effort, driver-agnostic detection of a Postgres EXCLUDE constraint
    violation (SQLSTATE 23P01), mirroring the existing `_is_unique_violation`
    helper in asset_service.py so both use the same "inspect exc.orig's
    string form" approach rather than importing asyncpg error types into the
    application layer.
    """
    message = str(getattr(exc, "orig", exc)).lower()
    return ("exclusion" in message or "23p01" in message) and constraint_hint.lower() in message
