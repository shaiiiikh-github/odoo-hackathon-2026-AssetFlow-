from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.api.dependencies import get_db, RoleChecker, get_current_user
from app.infrastructure.database.models import UserRole, User
from app.domain.enums import AssetStatus
from app.schemas.assets import AssetCreate, AssetResponse, AssetStatusUpdate
from app.services.asset_service import AssetService

router = APIRouter(prefix="/assets", tags=["Assets"])

# RBAC Definitions
require_asset_manager = RoleChecker([UserRole.ADMIN, UserRole.ASSET_MANAGER])

@router.post("/", response_model=AssetResponse, status_code=201, dependencies=[Depends(require_asset_manager)])
def register_new_asset(asset_in: AssetCreate, db: Session = Depends(get_db)):
    """
    Registers a new asset. Auto-generates Asset Tag. 
    Restricted to Admins and Asset Managers.
    """
    service = AssetService(db)
    return service.register_asset(asset_in)

@router.get("/", response_model=List[AssetResponse])
def get_assets(
    tag: Optional[str] = Query(None, description="Search by Asset Tag"),
    category_id: Optional[uuid.UUID] = Query(None, description="Filter by Category"),
    status: Optional[AssetStatus] = Query(None, description="Filter by Status"),
    department_id: Optional[uuid.UUID] = Query(None, description="Filter by currently holding Department"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # All authenticated users can view directory
):
    """
    Directory search with dynamic filters.
    """
    service = AssetService(db)
    return service.search_assets(
        tag=tag, 
        category_id=str(category_id) if category_id else None, 
        status=status, 
        department_id=str(department_id) if department_id else None
    )

@router.patch("/{asset_id}/status", response_model=AssetResponse, dependencies=[Depends(require_asset_manager)])
def change_asset_status(asset_id: uuid.UUID, status_update: AssetStatusUpdate, db: Session = Depends(get_db)):
    """
    Manually overrides asset status. Protected by strict state machine rules.
    """
    service = AssetService(db)
    return service.update_asset_status(str(asset_id), status_update)