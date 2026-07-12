from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.infrastructure.database.operations_models import AuditCycle, AuditItem
from app.infrastructure.database.asset_models import Asset
from app.domain.enums import AuditCycleStatus, AuditItemStatus, AssetStatus, AssetCondition

class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def close_audit_cycle(self, cycle_id: str) -> dict:
        """
        Closes an audit cycle. Automatically resolves discrepancies by updating 
        the master asset directory (e.g., marking unverified items as LOST).
        """
        cycle = self.db.query(AuditCycle).filter(AuditCycle.id == cycle_id).with_for_update().first()
        
        if not cycle:
            raise HTTPException(status_code=404, detail="Audit cycle not found")
            
        if cycle.status == AuditCycleStatus.CLOSED:
            raise HTTPException(status_code=400, detail="Audit cycle is already closed")

        # Fetch all discrepancies (Missing or Damaged) for this cycle
        discrepancies = self.db.query(AuditItem).filter(
            AuditItem.audit_cycle_id == cycle.id,
            AuditItem.status.in_([AuditItemStatus.MISSING, AuditItemStatus.DAMAGED])
        ).all()

        updated_assets_count = 0

        # Process discrepancies and update the core Assets
        for item in discrepancies:
            # Pessimistic lock on each asset being updated
            asset = self.db.query(Asset).filter(Asset.id == item.asset_id).with_for_update().first()
            if not asset:
                continue

            if item.status == AuditItemStatus.MISSING:
                # If an item wasn't found during audit, flag it as lost in the system
                if asset.status != AssetStatus.LOST:
                    asset.status = AssetStatus.LOST
                    updated_assets_count += 1
                    
            elif item.status == AuditItemStatus.DAMAGED:
                # If audited as damaged, update condition (maintenance can be raised separately)
                if asset.condition != AssetCondition.BROKEN:
                    asset.condition = AssetCondition.BROKEN
                    updated_assets_count += 1

        # Close the cycle
        cycle.status = AuditCycleStatus.CLOSED
        cycle.end_date = datetime.utcnow()

        self.db.commit()
        
        return {
            "message": "Audit cycle closed successfully.",
            "discrepancies_processed": len(discrepancies),
            "assets_updated": updated_assets_count
        }