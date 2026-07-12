from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.audit import AuditAssignment, AuditCycle, AuditFinding


class IAuditRepository(ABC):
    # --- cycles -------------------------------------------------------------
    @abstractmethod
    async def add_cycle(self, cycle: AuditCycle) -> AuditCycle:
        ...

    @abstractmethod
    async def get_cycle_by_id(self, cycle_id: UUID) -> AuditCycle | None:
        ...

    @abstractmethod
    async def get_cycle_by_id_for_update(self, cycle_id: UUID) -> AuditCycle | None:
        """
        SELECT ... FOR UPDATE on the cycle row. Held for the duration of
        close_cycle() so no finding can be inserted/updated concurrently
        with the close — see AuditService.close_cycle.
        """
        ...

    @abstractmethod
    async def close_cycle(self, cycle_id: UUID, closed_by_user_id: UUID) -> None:
        ...

    # --- auditor assignments --------------------------------------------------
    @abstractmethod
    async def add_assignment(self, assignment: AuditAssignment) -> AuditAssignment:
        ...

    @abstractmethod
    async def is_auditor_assigned(self, cycle_id: UUID, user_id: UUID) -> bool:
        ...

    @abstractmethod
    async def list_assignments(self, cycle_id: UUID) -> list[AuditAssignment]:
        ...

    # --- findings ------------------------------------------------------------
    @abstractmethod
    async def upsert_finding(self, finding: AuditFinding) -> AuditFinding:
        """Insert a new finding, or overwrite the existing (cycle_id, asset_id) row if one exists."""
        ...

    @abstractmethod
    async def get_finding(self, cycle_id: UUID, asset_id: UUID) -> AuditFinding | None:
        ...

    @abstractmethod
    async def list_findings_for_cycle(self, cycle_id: UUID) -> list[AuditFinding]:
        ...
