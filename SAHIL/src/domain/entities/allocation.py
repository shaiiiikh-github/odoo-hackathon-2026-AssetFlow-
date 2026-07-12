from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from uuid import UUID


class AllocationStatus(str, Enum):
    ACTIVE = "ACTIVE"          # asset is currently held by holder_user_id/holder_department_id
    RETURNED = "RETURNED"      # closed via return flow
    TRANSFERRED = "TRANSFERRED"  # closed via an approved transfer (superseded by a new allocation row)


class TransferStatus(str, Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class Allocation:
    """
    Pure domain entity for a single custody period of an asset.

    Exactly one row per asset may have status=ACTIVE at any time — that
    invariant is enforced in two places, deliberately:
      1. Application layer: AllocationService takes a row lock on the asset
         (SELECT ... FOR UPDATE) before checking/creating an allocation.
      2. Database layer: a partial unique index on
         allocations(asset_id) WHERE status = 'ACTIVE' (see migration 0003).
    The DB constraint is the actual source of truth; the app-layer lock exists
    to turn the failure mode from "ugly IntegrityError" into a clean domain
    exception with the current holder's identity attached.
    """

    id: UUID
    asset_id: UUID
    holder_user_id: UUID | None          # allocated to an individual employee
    holder_department_id: UUID | None    # allocated to a department (holder_user_id may be None)
    allocated_by_user_id: UUID
    status: AllocationStatus
    expected_return_date: date | None = None
    allocated_at: datetime = field(default_factory=datetime.utcnow)
    returned_at: datetime | None = None
    return_condition_notes: str | None = None

    def is_overdue(self, as_of: date | None = None) -> bool:
        reference = as_of or datetime.utcnow().date()
        return (
            self.status == AllocationStatus.ACTIVE
            and self.expected_return_date is not None
            and reference > self.expected_return_date
        )


@dataclass
class TransferRequest:
    """
    Requested -> Approved/Rejected workflow that runs alongside an existing
    ACTIVE allocation. Approval is the only path that ever closes the old
    allocation row and opens a new one — a transfer never mutates an
    allocation's holder in place, so the audit trail (who held what, when)
    stays intact.
    """

    id: UUID
    asset_id: UUID
    from_allocation_id: UUID
    requested_by_user_id: UUID
    requested_for_user_id: UUID | None
    requested_for_department_id: UUID | None
    status: TransferStatus
    requested_at: datetime = field(default_factory=datetime.utcnow)
    resolved_by_user_id: UUID | None = None
    resolved_at: datetime | None = None
    resolution_notes: str | None = None
