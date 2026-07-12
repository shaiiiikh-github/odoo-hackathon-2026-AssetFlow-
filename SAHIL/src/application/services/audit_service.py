from __future__ import annotations

import uuid
from datetime import date, datetime

from src.application.interfaces.i_unit_of_work import IUnitOfWork
from src.domain.entities.asset import AssetCondition, AssetStatus
from src.domain.entities.audit import (
    DISCREPANCY_STATUSES,
    AuditAssignment,
    AuditCycle,
    AuditCycleStatus,
    AuditFinding,
    AuditFindingStatus,
    DiscrepancyReportEntry,
)
from src.domain.entities.user import User
from src.domain.exceptions.domain_exceptions import (
    AuditCycleClosedError,
    EntityNotFoundError,
    InsufficientPermissionError,
    NotAnAssignedAuditorError,
)
from src.domain.state_machines.asset_state_machine import AssetStateMachine


class AuditService:
    """
    Owns audit cycle creation/assignment, auditor findings, the discrepancy
    report, and — the interesting cross-module part — closing a cycle,
    which pushes MISSING findings into the asset lifecycle as LOST and
    DAMAGED findings into the asset's condition field.

    Separation of concerns: identical convention to MaintenanceService —
    this service imports AssetStateMachine directly and mutates Asset
    entities via `uow.assets`, never via AssetService. AuditService,
    AllocationService, and MaintenanceService are three independent
    orchestrators that all share the same Asset entity + AssetStateMachine
    + IAssetRepository contract; none of them import each other, so the
    dependency graph among application services stays flat (every service
    depends on domain + IUnitOfWork only — never on a sibling service).

    Concurrency: closing a cycle is the one operation here that touches
    many asset rows in a single transaction. To avoid deadlocking against
    AllocationService/MaintenanceService (which each lock exactly one asset
    at a time) or against a second concurrent close of an overlapping
    cycle, every asset row this method locks is locked in a fixed order
    (ascending asset_id) — see close_cycle for why that ordering rule is
    what actually prevents deadlocks once more than one lock is held at a
    time in the same transaction.
    """

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    # ---------------------------------------------------------------- Cycle lifecycle
    async def create_cycle(
        self,
        *,
        acting_user: User,
        name: str,
        department_id: uuid.UUID | None,
        location: str | None,
        start_date: date,
        end_date: date,
        auditor_user_ids: list[uuid.UUID],
    ) -> AuditCycle:
        if not acting_user.can_manage_organization():
            raise InsufficientPermissionError(required_roles=["ADMIN"])

        async with self._uow as uow:
            cycle = AuditCycle(
                id=uuid.uuid4(),
                name=name.strip(),
                department_id=department_id,
                location=location,
                start_date=start_date,
                end_date=end_date,
                status=AuditCycleStatus.OPEN,
                created_by_user_id=acting_user.id,
            )
            created = await uow.audits.add_cycle(cycle)

            for auditor_id in dict.fromkeys(auditor_user_ids):  # de-dupe, preserve order
                assignment = AuditAssignment(id=uuid.uuid4(), cycle_id=created.id, auditor_user_id=auditor_id)
                await uow.audits.add_assignment(assignment)

            await uow.commit()
            return created

    async def assign_auditor(self, *, acting_user: User, cycle_id: uuid.UUID, auditor_user_id: uuid.UUID) -> AuditAssignment:
        if not acting_user.can_manage_organization():
            raise InsufficientPermissionError(required_roles=["ADMIN"])

        async with self._uow as uow:
            cycle = await uow.audits.get_cycle_by_id(cycle_id)
            if cycle is None:
                raise EntityNotFoundError("AuditCycle", str(cycle_id))
            if cycle.status != AuditCycleStatus.OPEN:
                raise AuditCycleClosedError(str(cycle_id))

            assignment = AuditAssignment(id=uuid.uuid4(), cycle_id=cycle_id, auditor_user_id=auditor_user_id)
            created = await uow.audits.add_assignment(assignment)
            await uow.commit()
            return created

    # ---------------------------------------------------------------- Findings
    async def submit_finding(
        self,
        *,
        acting_user: User,
        cycle_id: uuid.UUID,
        asset_id: uuid.UUID,
        finding_status: AuditFindingStatus,
        notes: str | None,
    ) -> AuditFinding:
        async with self._uow as uow:
            # Lock the cycle first so a finding submission can never
            # interleave with a concurrent close_cycle() call — either the
            # finding commits before the close sees it, or it blocks until
            # the close finishes and then gets rejected by the status check
            # below. This is the same "lock the parent, then act" ordering
            # used by AllocationService (asset) and MaintenanceService
            # (asset) — here the parent is the cycle instead of the asset.
            cycle = await uow.audits.get_cycle_by_id_for_update(cycle_id)
            if cycle is None:
                raise EntityNotFoundError("AuditCycle", str(cycle_id))
            if cycle.status != AuditCycleStatus.OPEN:
                raise AuditCycleClosedError(str(cycle_id))

            if not await uow.audits.is_auditor_assigned(cycle_id, acting_user.id):
                raise NotAnAssignedAuditorError(str(cycle_id))

            asset = await uow.assets.get_by_id(asset_id)  # existence check only, no lock needed for a finding write
            if asset is None:
                raise EntityNotFoundError("Asset", str(asset_id))

            finding = AuditFinding(
                id=uuid.uuid4(),
                cycle_id=cycle_id,
                asset_id=asset_id,
                marked_by_user_id=acting_user.id,
                status=finding_status,
                notes=notes,
            )
            # Upsert: an auditor correcting an earlier mis-click for the
            # same asset overwrites their previous finding rather than
            # creating a duplicate row (uq_audit_finding_cycle_asset).
            saved = await uow.audits.upsert_finding(finding)
            await uow.commit()
            return saved

    async def get_discrepancy_report(self, *, cycle_id: uuid.UUID) -> list[DiscrepancyReportEntry]:
        """
        Assembled live from findings + assets, filtered to MISSING/DAMAGED —
        callable any time during an OPEN cycle for a running view, and
        still callable after CLOSE for the permanent record (findings are
        frozen at that point, so the report becomes stable automatically).
        """
        async with self._uow as uow:
            cycle = await uow.audits.get_cycle_by_id(cycle_id)
            if cycle is None:
                raise EntityNotFoundError("AuditCycle", str(cycle_id))

            findings = await uow.audits.list_findings_for_cycle(cycle_id)
            entries: list[DiscrepancyReportEntry] = []
            for finding in findings:
                if finding.status not in DISCREPANCY_STATUSES:
                    continue
                asset = await uow.assets.get_by_id(finding.asset_id)
                if asset is None:
                    continue
                entries.append(
                    DiscrepancyReportEntry(
                        asset_id=finding.asset_id,
                        asset_tag=asset.asset_tag,
                        finding_status=finding.status,
                        marked_by_user_id=finding.marked_by_user_id,
                        notes=finding.notes,
                        marked_at=finding.marked_at,
                    )
                )
            return entries

    # ---------------------------------------------------------------- Read-only queries
    async def get_cycle(self, cycle_id: uuid.UUID) -> AuditCycle | None:
        async with self._uow as uow:
            return await uow.audits.get_cycle_by_id(cycle_id)

    async def list_assignments(self, cycle_id: uuid.UUID) -> list[AuditAssignment]:
        async with self._uow as uow:
            return await uow.audits.list_assignments(cycle_id)

    async def list_findings(self, cycle_id: uuid.UUID) -> list[AuditFinding]:
        async with self._uow as uow:
            return await uow.audits.list_findings_for_cycle(cycle_id)

    # ---------------------------------------------------------------- Close cycle (the cross-module orchestration)
    async def close_cycle(self, *, acting_user: User, cycle_id: uuid.UUID) -> AuditCycle:
        """
        This is the method the Phase 4 brief means by "Audit module updating
        Asset module": closing a cycle locks the cycle's records AND pushes
        each flagged finding's consequence into the asset lifecycle —
        MISSING -> asset status LOST (via AssetStateMachine, so an asset
        already RETIRED/DISPOSED can't be silently overwritten — that
        finding is skipped and left for a human to reconcile rather than
        raising and aborting the whole close), DAMAGED -> asset.condition
        set to DAMAGED (a condition-only update; DAMAGED isn't a lifecycle
        state, so no state-machine transition applies here).

        Everything below happens inside ONE transaction: the cycle only
        flips to CLOSED after every asset-side update in this pass has
        succeeded, so a failure partway through leaves the cycle OPEN and
        no assets partially updated, rather than a half-applied audit.
        """
        if not acting_user.can_manage_organization():
            raise InsufficientPermissionError(required_roles=["ADMIN"])

        async with self._uow as uow:
            cycle = await uow.audits.get_cycle_by_id_for_update(cycle_id)
            if cycle is None:
                raise EntityNotFoundError("AuditCycle", str(cycle_id))
            if cycle.status != AuditCycleStatus.OPEN:
                raise AuditCycleClosedError(str(cycle_id))

            findings = await uow.audits.list_findings_for_cycle(cycle_id)
            flagged = [f for f in findings if f.status in DISCREPANCY_STATUSES]

            # Lock every affected asset in a fixed order (ascending id)
            # BEFORE mutating any of them. This is what makes multi-asset
            # locking safe: if two transactions each need locks on assets
            # {A, B}, both acquiring in the same fixed order means neither
            # can end up holding A-waiting-for-B while the other holds
            # B-waiting-for-A — the classic deadlock shape is structurally
            # impossible when every locker agrees on one global order.
            for finding in sorted(flagged, key=lambda f: str(f.asset_id)):
                asset = await uow.assets.get_by_id_for_update(finding.asset_id)
                if asset is None:
                    continue  # asset was deleted since the finding was recorded; skip, don't fail the whole close

                if finding.status == AuditFindingStatus.MISSING:
                    if AssetStateMachine.can_transition(asset.status, AssetStatus.LOST):
                        previous_status = asset.status
                        AssetStateMachine.transition(asset, AssetStatus.LOST)
                        await uow.assets.update(asset)
                        await uow.assets.record_state_transition(
                            asset_id=asset.id,
                            from_state=previous_status,
                            to_state=AssetStatus.LOST,
                            triggered_by_user_id=acting_user.id,
                            reason=f"Confirmed missing in audit cycle {cycle_id}",
                        )
                    # else: asset already in a terminal state (RETIRED/DISPOSED/
                    # already LOST) — leave it as-is rather than raising and
                    # aborting the whole cycle close over one stale finding.

                elif finding.status == AuditFindingStatus.DAMAGED:
                    asset.condition = AssetCondition.DAMAGED
                    await uow.assets.update(asset)

            await uow.audits.close_cycle(cycle_id, closed_by_user_id=acting_user.id)
            await uow.commit()

            cycle.status = AuditCycleStatus.CLOSED
            cycle.closed_by_user_id = acting_user.id
            cycle.closed_at = datetime.utcnow()
            return cycle
