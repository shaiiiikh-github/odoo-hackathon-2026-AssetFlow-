from __future__ import annotations

from fastapi import Depends

from src.application.interfaces.i_unit_of_work import IUnitOfWork
from src.application.services.allocation_service import AllocationService
from src.application.services.asset_service import AssetService
from src.application.services.audit_service import AuditService
from src.application.services.auth_service import AuthService
from src.application.services.booking_service import BookingService
from src.application.services.employee_directory_service import EmployeeDirectoryService
from src.application.services.maintenance_service import MaintenanceService
from src.application.services.organization_service import OrganizationService
from src.presentation.middleware.auth_middleware import get_unit_of_work


def get_auth_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> AuthService:
    return AuthService(uow)


def get_organization_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> OrganizationService:
    return OrganizationService(uow)


def get_employee_directory_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> EmployeeDirectoryService:
    return EmployeeDirectoryService(uow)


def get_asset_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> AssetService:
    return AssetService(uow)


def get_allocation_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> AllocationService:
    return AllocationService(uow)


def get_booking_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> BookingService:
    return BookingService(uow)


def get_maintenance_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> MaintenanceService:
    return MaintenanceService(uow)


def get_audit_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> AuditService:
    return AuditService(uow)
