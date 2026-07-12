from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.entities.booking import Booking, BookingStatus


class IBookingRepository(ABC):
    @abstractmethod
    async def find_overlapping(self, asset_id: UUID, start_time: datetime, end_time: datetime) -> list[Booking]:
        """
        App-level pre-check used to return a friendly, specific error
        ("overlaps with your 9:00-10:00 booking") before we even attempt the
        insert. This is NOT what prevents the race — see `create_booking`.
        """
        ...

    @abstractmethod
    async def create_booking(self, booking: Booking) -> Booking:
        """
        Inserts the row. The actual overlap-freedom guarantee under
        concurrency comes from the `EXCLUDE USING gist` constraint on the
        bookings table (migration 0003), which Postgres enforces atomically
        as part of this INSERT. Implementations must let the resulting
        exclusion-violation propagate as a raw exception for the service
        layer to translate into SlotOverlapError — never swallow it here.
        """
        ...

    @abstractmethod
    async def get_by_id(self, booking_id: UUID) -> Booking | None:
        ...

    @abstractmethod
    async def cancel(self, booking_id: UUID) -> None:
        ...

    @abstractmethod
    async def get_for_asset(self, asset_id: UUID, from_time: datetime | None, to_time: datetime | None) -> list[Booking]:
        ...
