from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.i_booking_repository import IBookingRepository
from src.domain.entities.booking import ACTIVE_BOOKING_STATUSES, Booking, BookingStatus
from src.infrastructure.database.models.booking_model import BookingModel


class SqlAlchemyBookingRepository(IBookingRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: BookingModel) -> Booking:
        return Booking(
            id=model.id,
            asset_id=model.asset_id,
            booked_by_user_id=model.booked_by_user_id,
            department_id=model.department_id,
            start_time=model.start_time,
            end_time=model.end_time,
            status=model.status,
            purpose=model.purpose,
            created_at=model.created_at,
            cancelled_at=model.cancelled_at,
        )

    async def find_overlapping(self, asset_id: UUID, start_time: datetime, end_time: datetime) -> list[Booking]:
        """
        The ORM overlap query. For half-open intervals [a_start, a_end) and
        [b_start, b_end), they overlap iff a_start < b_end AND b_start < a_end.
        This is the standard interval-overlap test — note it correctly
        allows back-to-back bookings (10:00-11:00 immediately after
        9:00-10:00 is NOT an overlap, since 10:00 < 10:00 is false).

        This SELECT is a pre-check for a friendly error message only. It is
        run with NO row lock and provides no concurrency guarantee by
        itself — two transactions can both run this, both see "no overlap",
        and both attempt to INSERT at the same instant. The actual
        correctness guarantee is the `no_overlapping_bookings` EXCLUDE
        constraint enforced by Postgres on the INSERT (see create_booking).
        """
        stmt = select(BookingModel).where(
            BookingModel.asset_id == asset_id,
            BookingModel.status.in_(ACTIVE_BOOKING_STATUSES),
            and_(
                BookingModel.start_time < end_time,
                start_time < BookingModel.end_time,
            ),
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create_booking(self, booking: Booking) -> Booking:
        model = BookingModel(
            id=booking.id,
            asset_id=booking.asset_id,
            booked_by_user_id=booking.booked_by_user_id,
            department_id=booking.department_id,
            start_time=booking.start_time,
            end_time=booking.end_time,
            status=booking.status,
            purpose=booking.purpose,
        )
        self._session.add(model)
        # flush (not commit) inside the caller's transaction: if this row
        # violates `no_overlapping_bookings`, Postgres raises here as an
        # IntegrityError (asyncpg.exceptions.ExclusionViolationError under
        # the hood) and BookingService translates it into SlotOverlapError.
        # This flush is what actually enforces atomicity — not the earlier
        # find_overlapping() pre-check.
        await self._session.flush()
        return self._to_entity(model)

    async def get_by_id(self, booking_id: UUID) -> Booking | None:
        model = await self._session.get(BookingModel, booking_id)
        return self._to_entity(model) if model else None

    async def cancel(self, booking_id: UUID) -> None:
        model = await self._session.get(BookingModel, booking_id)
        if model is None:
            raise ValueError(f"Booking {booking_id} does not exist.")
        model.status = BookingStatus.CANCELLED
        model.cancelled_at = datetime.utcnow()
        await self._session.flush()

    async def get_for_asset(self, asset_id: UUID, from_time: datetime | None, to_time: datetime | None) -> list[Booking]:
        stmt = select(BookingModel).where(BookingModel.asset_id == asset_id)
        if from_time is not None:
            stmt = stmt.where(BookingModel.end_time > from_time)
        if to_time is not None:
            stmt = stmt.where(BookingModel.start_time < to_time)
        stmt = stmt.order_by(BookingModel.start_time.asc())
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]
