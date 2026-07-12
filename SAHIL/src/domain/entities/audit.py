from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from uuid import UUID


class AuditCycleStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class AuditFindingStatus(str, Enum):
    PENDING = "PENDING"      # auditor hasn't checked this asset yet
    VERIFIED = "VERIFIED"
    MISSING = "MISSING"
    DAMAGED = "DAMAGED"


# Findings in these states are what the discrepancy report surfaces, and
# what closing a cycle acts on. Kept as a single named set so the report
# query and the close-cycle orchestration can't silently drift apart.
DISCREPANCY_STATUSES: frozenset[AuditFindingStatus] = frozenset(
    {AuditFindingStatus.MISSING, AuditFindingStatus.DAMAGED}
)


@dataclass
class AuditCycle:
    """
    A scoped verification run (by department and/or location, over a date
    range). `status` flips to CLOSED exactly once, via
    AuditService.close_cycle — after that, findings become immutable
    (enforced at the service layer: any write path checks
    cycle.status == OPEN before touching a finding).
    """

    id: UUID
    name: str
    department_id: UUID | None
    location: str | None
    start_date: date
    end_date: date
    status: AuditCycleStatus
    created_by_user_id: UUID
    created_at: datetime = field(default_factory=datetime.utcnow)
    closed_by_user_id: UUID | None = None
    closed_at: datetime | None = None


@dataclass
class AuditAssignment:
    """One row per auditor assigned to a cycle. A cycle can have several auditors."""

    id: UUID
    cycle_id: UUID
    auditor_user_id: UUID
    assigned_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AuditFinding:
    """
    One row per (cycle, asset) pair — the auditor's verdict. Upsertable while
    the cycle is OPEN (an auditor can correct a mis-click before the cycle
    closes); frozen the instant the cycle closes. This *is* the audit
    history for the cycle — no separate history table is needed since
    findings are themselves never deleted, only ever superseded by an
    updated row while still OPEN.
    """

    id: UUID
    cycle_id: UUID
    asset_id: UUID
    marked_by_user_id: UUID
    status: AuditFindingStatus
    notes: str | None = None
    marked_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DiscrepancyReportEntry:
    """
    Read-model DTO — not a persisted row. Assembled on demand by
    AuditService.get_discrepancy_report by joining findings to assets, so
    the report always reflects the live state of findings without a second
    copy of the data to keep in sync.
    """

    asset_id: UUID
    asset_tag: str
    finding_status: AuditFindingStatus
    marked_by_user_id: UUID
    notes: str | None
    marked_at: datetime
