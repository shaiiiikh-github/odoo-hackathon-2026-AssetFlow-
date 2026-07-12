from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from src.application.services.audit_service import AuditService
from src.domain.entities.user import User
from src.domain.exceptions.domain_exceptions import EntityNotFoundError
from src.presentation.api.v1.schemas.audit_schemas import (
    AssignAuditorRequest,
    AuditCycleResponse,
    AuditFindingResponse,
    CreateAuditCycleRequest,
    DiscrepancyReportEntryResponse,
    SubmitFindingRequest,
)
from src.presentation.dependencies import get_audit_service
from src.presentation.middleware.auth_middleware import require_admin, require_any_authenticated

router = APIRouter(prefix="/audit-cycles", tags=["Asset Audit"])


@router.post("", response_model=AuditCycleResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_cycle(
    payload: CreateAuditCycleRequest,
    acting_user: User = Depends(require_admin),
    service: AuditService = Depends(get_audit_service),
) -> AuditCycleResponse:
    """Admin-only, per Screen 8: scopes the cycle to a department and/or location, over a date range, with named auditors."""
    cycle = await service.create_cycle(
        acting_user=acting_user,
        name=payload.name,
        department_id=payload.department_id,
        location=payload.location,
        start_date=payload.start_date,
        end_date=payload.end_date,
        auditor_user_ids=payload.auditor_user_ids,
    )
    return AuditCycleResponse.model_validate(cycle)


@router.get("/{cycle_id}", response_model=AuditCycleResponse)
async def get_audit_cycle(
    cycle_id: uuid.UUID,
    _: User = Depends(require_any_authenticated),
    service: AuditService = Depends(get_audit_service),
) -> AuditCycleResponse:
    cycle = await service.get_cycle(cycle_id)
    if cycle is None:
        raise EntityNotFoundError("AuditCycle", str(cycle_id))
    return AuditCycleResponse.model_validate(cycle)


@router.post("/{cycle_id}/auditors", status_code=status.HTTP_201_CREATED)
async def assign_auditor(
    cycle_id: uuid.UUID,
    payload: AssignAuditorRequest,
    acting_user: User = Depends(require_admin),
    service: AuditService = Depends(get_audit_service),
) -> dict[str, str]:
    await service.assign_auditor(acting_user=acting_user, cycle_id=cycle_id, auditor_user_id=payload.auditor_user_id)
    return {"status": "assigned"}


@router.post(
    "/{cycle_id}/findings", response_model=AuditFindingResponse, status_code=status.HTTP_201_CREATED
)
async def submit_finding(
    cycle_id: uuid.UUID,
    payload: SubmitFindingRequest,
    acting_user: User = Depends(require_any_authenticated),
    service: AuditService = Depends(get_audit_service),
) -> AuditFindingResponse:
    """
    Only an auditor assigned to this cycle may submit — enforced in
    AuditService, not by role, since 'auditor' is an assignment, not a
    fixed Role. Re-submitting for the same asset overwrites the prior
    verdict (upsert on cycle_id + asset_id) until the cycle is closed.
    """
    finding = await service.submit_finding(
        acting_user=acting_user,
        cycle_id=cycle_id,
        asset_id=payload.asset_id,
        finding_status=payload.finding_status,
        notes=payload.notes,
    )
    return AuditFindingResponse.model_validate(finding)


@router.get("/{cycle_id}/findings", response_model=list[AuditFindingResponse])
async def list_findings(
    cycle_id: uuid.UUID,
    _: User = Depends(require_any_authenticated),
    service: AuditService = Depends(get_audit_service),
) -> list[AuditFindingResponse]:
    findings = await service.list_findings(cycle_id)
    return [AuditFindingResponse.model_validate(f) for f in findings]


@router.get("/{cycle_id}/discrepancy-report", response_model=list[DiscrepancyReportEntryResponse])
async def get_discrepancy_report(
    cycle_id: uuid.UUID,
    _: User = Depends(require_any_authenticated),
    service: AuditService = Depends(get_audit_service),
) -> list[DiscrepancyReportEntryResponse]:
    """Live view of MISSING/DAMAGED findings — available while OPEN, and stable once the cycle is CLOSED."""
    report = await service.get_discrepancy_report(cycle_id=cycle_id)
    return [DiscrepancyReportEntryResponse.model_validate(e) for e in report]


@router.post("/{cycle_id}/close", response_model=AuditCycleResponse)
async def close_audit_cycle(
    cycle_id: uuid.UUID,
    acting_user: User = Depends(require_admin),
    service: AuditService = Depends(get_audit_service),
) -> AuditCycleResponse:
    """
    Locks the cycle and, in the same transaction, pushes MISSING findings to
    asset status LOST and DAMAGED findings to asset condition DAMAGED.
    """
    cycle = await service.close_cycle(acting_user=acting_user, cycle_id=cycle_id)
    return AuditCycleResponse.model_validate(cycle)
