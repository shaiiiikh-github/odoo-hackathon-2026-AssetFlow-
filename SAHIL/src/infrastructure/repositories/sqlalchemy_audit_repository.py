from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.i_audit_repository import IAuditRepository
from src.domain.entities.audit import AuditAssignment, AuditCycle, AuditCycleStatus, AuditFinding
from src.infrastructure.database.models.audit_models import AuditAssignmentModel, AuditCycleModel, AuditFindingModel


class SqlAlchemyAuditRepository(IAuditRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # --- mapping helpers -------------------------------------------------
    @staticmethod
    def _cycle_to_entity(model: AuditCycleModel) -> AuditCycle:
        return AuditCycle(
            id=model.id,
            name=model.name,
            department_id=model.department_id,
            location=model.location,
            start_date=model.start_date,
            end_date=model.end_date,
            status=model.status,
            created_by_user_id=model.created_by_user_id,
            created_at=model.created_at,
            closed_by_user_id=model.closed_by_user_id,
            closed_at=model.closed_at,
        )

    @staticmethod
    def _assignment_to_entity(model: AuditAssignmentModel) -> AuditAssignment:
        return AuditAssignment(
            id=model.id, cycle_id=model.cycle_id, auditor_user_id=model.auditor_user_id, assigned_at=model.assigned_at
        )

    @staticmethod
    def _finding_to_entity(model: AuditFindingModel) -> AuditFinding:
        return AuditFinding(
            id=model.id,
            cycle_id=model.cycle_id,
            asset_id=model.asset_id,
            marked_by_user_id=model.marked_by_user_id,
            status=model.status,
            notes=model.notes,
            marked_at=model.marked_at,
        )

    # --- cycles --------------------------------------------------------------
    async def add_cycle(self, cycle: AuditCycle) -> AuditCycle:
        model = AuditCycleModel(
            id=cycle.id,
            name=cycle.name,
            department_id=cycle.department_id,
            location=cycle.location,
            start_date=cycle.start_date,
            end_date=cycle.end_date,
            status=cycle.status,
            created_by_user_id=cycle.created_by_user_id,
        )
        self._session.add(model)
        await self._session.flush()
        return self._cycle_to_entity(model)

    async def get_cycle_by_id(self, cycle_id: UUID) -> AuditCycle | None:
        model = await self._session.get(AuditCycleModel, cycle_id)
        return self._cycle_to_entity(model) if model else None

    async def get_cycle_by_id_for_update(self, cycle_id: UUID) -> AuditCycle | None:
        stmt = select(AuditCycleModel).where(AuditCycleModel.id == cycle_id).with_for_update()
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._cycle_to_entity(model) if model else None

    async def close_cycle(self, cycle_id: UUID, closed_by_user_id: UUID) -> None:
        model = await self._session.get(AuditCycleModel, cycle_id)
        if model is None:
            raise ValueError(f"Audit cycle {cycle_id} does not exist.")
        model.status = AuditCycleStatus.CLOSED
        model.closed_by_user_id = closed_by_user_id
        model.closed_at = datetime.utcnow()
        await self._session.flush()

    # --- assignments -----------------------------------------------------
    async def add_assignment(self, assignment: AuditAssignment) -> AuditAssignment:
        model = AuditAssignmentModel(id=assignment.id, cycle_id=assignment.cycle_id, auditor_user_id=assignment.auditor_user_id)
        self._session.add(model)
        await self._session.flush()
        return self._assignment_to_entity(model)

    async def is_auditor_assigned(self, cycle_id: UUID, user_id: UUID) -> bool:
        stmt = select(AuditAssignmentModel.id).where(
            AuditAssignmentModel.cycle_id == cycle_id, AuditAssignmentModel.auditor_user_id == user_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def list_assignments(self, cycle_id: UUID) -> list[AuditAssignment]:
        stmt = select(AuditAssignmentModel).where(AuditAssignmentModel.cycle_id == cycle_id)
        result = await self._session.execute(stmt)
        return [self._assignment_to_entity(m) for m in result.scalars().all()]

    # --- findings ----------------------------------------------------------
    async def upsert_finding(self, finding: AuditFinding) -> AuditFinding:
        """
        A native `INSERT ... ON CONFLICT (cycle_id, asset_id) DO UPDATE`.
        This is the correct way to express "create or correct my verdict for
        this asset" under concurrency: two submissions racing for the same
        (cycle_id, asset_id) resolve atomically inside Postgres, rather than
        via a Python-level 'SELECT, then INSERT-or-UPDATE' that has a race
        window between the SELECT and the write.
        """
        stmt = pg_insert(AuditFindingModel).values(
            id=finding.id,
            cycle_id=finding.cycle_id,
            asset_id=finding.asset_id,
            marked_by_user_id=finding.marked_by_user_id,
            status=finding.status,
            notes=finding.notes,
        )
        stmt = stmt.on_conflict_do_update(
            constraint="uq_audit_finding_cycle_asset",
            set_={
                "marked_by_user_id": stmt.excluded.marked_by_user_id,
                "status": stmt.excluded.status,
                "notes": stmt.excluded.notes,
                "marked_at": datetime.utcnow(),
            },
        ).returning(AuditFindingModel)
        result = await self._session.execute(stmt)
        await self._session.flush()
        model = result.scalar_one()
        return self._finding_to_entity(model)

    async def get_finding(self, cycle_id: UUID, asset_id: UUID) -> AuditFinding | None:
        stmt = select(AuditFindingModel).where(
            AuditFindingModel.cycle_id == cycle_id, AuditFindingModel.asset_id == asset_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._finding_to_entity(model) if model else None

    async def list_findings_for_cycle(self, cycle_id: UUID) -> list[AuditFinding]:
        stmt = select(AuditFindingModel).where(AuditFindingModel.cycle_id == cycle_id)
        result = await self._session.execute(stmt)
        return [self._finding_to_entity(m) for m in result.scalars().all()]
