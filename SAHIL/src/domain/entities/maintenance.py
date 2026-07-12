from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID


class MaintenancePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class MaintenanceStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    TECHNICIAN_ASSIGNED = "TECHNICIAN_ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


@dataclass
class MaintenanceRequest:
    """
    Pure domain entity. Status transitions are never applied by mutating
    `.status` directly — always via `MaintenanceStateMachine.transition(...)`,
    mirroring the AssetStateMachine convention from Phase 2/3. The one place
    this workflow reaches outside itself is the moment of APPROVED (asset ->
    UNDER_MAINTENANCE) and RESOLVED (asset -> AVAILABLE); that cross-module
    call is owned entirely by MaintenanceService, never by this entity or by
    AssetService, keeping the dependency direction one-way
    (maintenance -> asset, never the reverse).
    """

    id: UUID
    asset_id: UUID
    raised_by_user_id: UUID
    issue_description: str
    priority: MaintenancePriority
    status: MaintenanceStatus
    photo_url: str | None = None
    approved_by_user_id: UUID | None = None
    rejection_reason: str | None = None
    # Technicians are frequently external/contracted and not app users, so
    # we record them as free-text rather than a User FK.
    assigned_technician_name: str | None = None
    assigned_technician_contact: str | None = None
    resolution_notes: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: datetime | None = None

    def apply_transition(self, new_status: MaintenanceStatus) -> None:
        """Called only by MaintenanceStateMachine after it has validated legality."""
        self.status = new_status
