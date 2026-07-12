from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID


class BookingStatus(str, Enum):
    UPCOMING = "UPCOMING"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# Bookings in these states occupy the timeline and must be checked for
# overlap. CANCELLED/COMPLETED bookings are historical and don't block
# new slots — this list drives both the app-level overlap query AND the
# database EXCLUDE constraint's partial WHERE clause (see migration 0003),
# so the two must be changed together if this ever changes.
ACTIVE_BOOKING_STATUSES: frozenset[BookingStatus] = frozenset({BookingStatus.UPCOMING, BookingStatus.ONGOING})


@dataclass
class Booking:
    """
    Pure domain entity for a single time-slot reservation of a bookable
    resource (asset with is_bookable=True).

    Overlap-freedom for a given asset_id across UPCOMING/ONGOING bookings is
    a hard invariant, enforced at the database level by a PostgreSQL EXCLUDE
    constraint over (asset_id, time_range) — see migration 0003 for the exact
    DDL. That constraint, not any application check, is what makes the
    guarantee airtight under concurrency.
    """

    id: UUID
    asset_id: UUID
    booked_by_user_id: UUID
    start_time: datetime   # timezone-aware (UTC)
    end_time: datetime     # timezone-aware (UTC)
    status: BookingStatus
    department_id: UUID | None = None   # set when booked on behalf of a department
    purpose: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    cancelled_at: datetime | None = None

    def overlaps(self, start: datetime, end: datetime) -> bool:
        """Half-open interval overlap check: [start, end) vs [self.start, self.end)."""
        return self.start_time < end and start < self.end_time
