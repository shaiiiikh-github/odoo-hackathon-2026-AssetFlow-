from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid
from typing import Optional, List

from app.infrastructure.database.asset_models import Asset
from app.infrastructure.database.models import Department, User
# Assuming AssetAllocation exists in models
# from app.infrastructure.database.allocation_models import AssetAllocation 
from app.schemas.assets import AssetCreate, AssetStatusUpdate
from app.domain.state_machine import AssetStateMachine
from app.domain.enums import AssetStatus

class AssetService:
    def __init__(self, db: Session):
        self.db = db

    def generate_asset_tag(self, category_id: str) -> str:
        """Generates a unique tag, e.g., AF-A8F93B"""
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"AF-{unique_suffix}"

    def register_asset(self, asset_in: AssetCreate) -> Asset:
        # Edge Case: Check for duplicate serial number proactively
        existing_asset = self.db.query(Asset).filter(Asset.serial_number == asset_in.serial_number).first()
        if existing_asset:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Asset with serial number {asset_in.serial_number} already exists."
            )
            
        asset = Asset(
            **asset_in.model_dump(),
            asset_tag=self.generate_asset_tag(str(asset_in.category_id)),
            status=AssetStatus.AVAILABLE # Enforce starting state
        )
        
        try:
            self.db.add(asset)
            self.db.commit()
            self.db.refresh(asset)
            return asset
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Database integrity error during asset registration.")

    def update_asset_status(self, asset_id: str, status_update: AssetStatusUpdate) -> Asset:
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        # Delegate validation to the Domain layer State Machine
        AssetStateMachine.validate_transition(asset.status, status_update.status)

        asset.status = status_update.status
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def search_assets(
        self, 
        tag: Optional[str] = None, 
        category_id: Optional[str] = None, 
        status: Optional[AssetStatus] = None,
        department_id: Optional[str] = None
    ) -> List[Asset]:
        """
        Optimized search endpoint with dynamic filtering.
        """
        query = self.db.query(Asset)

        if tag:
            query = query.filter(Asset.asset_tag.ilike(f"%{tag}%"))
        if category_id:
            query = query.filter(Asset.category_id == category_id)
        if status:
            query = query.filter(Asset.status == status)
            
        if department_id:
            # We must join with allocations and users to filter by department correctly
            # Note: Requires AssetAllocation model to be imported
            pass 
            # query = query.join(AssetAllocation).join(User, AssetAllocation.assigned_to_user_id == User.id)\
            #              .filter((AssetAllocation.assigned_to_dept_id == department_id) | 
            #                      (User.department_id == department_id))\
            #              .filter(AssetAllocation.status == 'ACTIVE')

        return query.all()