from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.infrastructure.database.operations_models import MaintenanceRequest
from app.infrastructure.database.asset_models import Asset
from app.domain.enums import MaintenanceStatus, AssetStatus
from app.domain.state_machine import AssetStateMachine

class MaintenanceService:
    def __init__(self, db: Session):
        self.db = db

    def approve_maintenance(self, request_id: str, approved_by_id: str) -> MaintenanceRequest:
        """
        Approves a maintenance request and transitions the associated asset to 'UNDER_MAINTENANCE'.
        """
        request = self.db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).with_for_update().first()
        if not request:
            raise HTTPException(status_code=404, detail="Maintenance Request not found")

        if request.status != MaintenanceStatus.PENDING:
            raise HTTPException(status_code=400, detail="Only pending requests can be approved.")

        # Lock the associated asset to update its status safely
        asset = self.db.query(Asset).filter(Asset.id == request.asset_id).with_for_update().first()
        
        # Cross-Module Side Effect: Validate and update core Asset status
        AssetStateMachine.validate_transition(asset.status, AssetStatus.UNDER_MAINTENANCE)
        
        asset.status = AssetStatus.UNDER_MAINTENANCE
        request.status = MaintenanceStatus.APPROVED
        request.approved_by_id = approved_by_id

        self.db.commit()
        self.db.refresh(request)
        return request

    def resolve_maintenance(self, request_id: str) -> MaintenanceRequest:
        """
        Marks maintenance as resolved and frees up the asset.
        """
        request = self.db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).with_for_update().first()
        
        if request.status not in [MaintenanceStatus.APPROVED, MaintenanceStatus.IN_PROGRESS]:
            raise HTTPException(status_code=400, detail="Invalid request state for resolution.")

        asset = self.db.query(Asset).filter(Asset.id == request.asset_id).with_for_update().first()
        AssetStateMachine.validate_transition(asset.status, AssetStatus.AVAILABLE)

        asset.status = AssetStatus.AVAILABLE
        request.status = MaintenanceStatus.RESOLVED
        request.resolved_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(request)
        return request