from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID


class AssetStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    ALLOCATED = "ALLOCATED"
    RESERVED = "RESERVED"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"
    LOST = "LOST"
    RETIRED = "RETIRED"
    DISPOSED = "DISPOSED"


class AssetCondition(str, Enum):
    NEW = "NEW"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"
    DAMAGED = "DAMAGED"


@dataclass
class Asset:
    """
    Pure domain entity. State transitions are NOT performed by mutating
    `.status` directly from outside — always go through
    `AssetStateMachine.transition(asset, to_state)` so the legality check
    can never be bypassed by a careless service call.
    """

    id: UUID
    asset_tag: str
    serial_number: str
    name: str
    category_id: UUID
    status: AssetStatus
    condition: AssetCondition
    location: str
    is_bookable: bool
    acquisition_date: date | None = None
    acquisition_cost: Decimal | None = None
    department_id: UUID | None = None          # current custodian department; kept in sync by Allocation module
    photo_url: str | None = None
    document_urls: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def apply_transition(self, new_status: AssetStatus) -> None:
        """Called only by the state machine after it has validated legality."""
        self.status = new_status
