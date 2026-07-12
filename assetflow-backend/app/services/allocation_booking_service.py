from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
import uuid

from app.infrastructure.database.asset_models import Asset
from app.infrastructure.database.transactional_models import AssetAllocation, ResourceBooking, AllocationStatus, BookingStatus
from app.domain.enums import AssetStatus

class AllocationBookingService:
    def __init__(self, db: Session):
        self.db = db

    def allocate_asset(self, asset_id: str, assign_to_user_id: str, allocated_by_id: str) -> AssetAllocation:
        """
        Allocates an asset to a user. Employs Pessimistic Locking to prevent double allocation.
        """
        # 1. PESSIMISTIC LOCK: Lock the asset row so no other transaction can allocate it right now
        asset = self.db.query(Asset).filter(Asset.id == asset_id).with_for_update().first()
        
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        # 2. Check State
        if asset.status == AssetStatus.ALLOCATED:
            # Requirements: Reject direct allocation and indicate Transfer Request workflow
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Asset is already allocated. Please initiate a Transfer Request."
            )
        elif asset.status != AssetStatus.AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Asset cannot be allocated. Current status: {asset.status}"
            )

        # 3. Process Allocation
        asset.status = AssetStatus.ALLOCATED
        
        allocation = AssetAllocation(
            asset_id=asset.id,
            assigned_to_user_id=assign_to_user_id,
            allocated_by_id=allocated_by_id,
            status=AllocationStatus.ACTIVE
        )
        
        self.db.add(allocation)
        self.db.commit() # Lock is released upon commit
        self.db.refresh(allocation)
        return allocation

    def book_resource(self, asset_id: str, booked_by_id: str, start_time: datetime, end_time: datetime) -> ResourceBooking:
        """
        Books a shared resource. Validates time-slot overlaps under a DB lock.
        """
        if start_time >= end_time:
            raise HTTPException(status_code=400, detail="Start time must be before end time.")

        # 1. PESSIMISTIC LOCK: Serialize all booking attempts for this specific asset
        asset = self.db.query(Asset).filter(Asset.id == asset_id).with_for_update().first()
        
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
            
        if not asset.is_shared_bookable:
            raise HTTPException(status_code=400, detail="This asset is not flagged as a bookable shared resource.")

        # 2. EXACT SQL/ORM LOGIC FOR OVERLAPS
        # Overlap formula: (Existing_Start < New_End) AND (Existing_End > New_Start)
        overlapping_booking = self.db.query(ResourceBooking).filter(
            ResourceBooking.asset_id == asset.id,
            ResourceBooking.status.in_([BookingStatus.UPCOMING, BookingStatus.ONGOING]),
            ResourceBooking.start_time < end_time,
            ResourceBooking.end_time > start_time
        ).first()

        if overlapping_booking:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Time slot overlaps with an existing booking from {overlapping_booking.start_time} to {overlapping_booking.end_time}."
            )

        # 3. Create Booking
        booking = ResourceBooking(
            asset_id=asset.id,
            booked_by_id=booked_by_id,
            start_time=start_time,
            end_time=end_time,
            status=BookingStatus.UPCOMING
        )
        
        self.db.add(booking)
        self.db.commit() # Lock is released upon commit
        self.db.refresh(booking)
        return booking