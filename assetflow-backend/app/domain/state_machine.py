from app.domain.enums import AssetStatus
from fastapi import HTTPException, status

class AssetStateMachine:
    """
    Enforces strict state transitions for assets to prevent logical errors 
    (e.g., transitioning from DISPOSED to ALLOCATED).
    """
    ALLOWED_TRANSITIONS = {
        AssetStatus.AVAILABLE: {
            AssetStatus.ALLOCATED, AssetStatus.RESERVED, 
            AssetStatus.UNDER_MAINTENANCE, AssetStatus.LOST, AssetStatus.RETIRED
        },
        AssetStatus.ALLOCATED: {
            AssetStatus.AVAILABLE, AssetStatus.UNDER_MAINTENANCE, AssetStatus.LOST
        },
        AssetStatus.RESERVED: {
            AssetStatus.AVAILABLE, AssetStatus.ALLOCATED
        },
        AssetStatus.UNDER_MAINTENANCE: {
            AssetStatus.AVAILABLE, AssetStatus.RETIRED, AssetStatus.DISPOSED
        },
        AssetStatus.LOST: {
            AssetStatus.AVAILABLE, AssetStatus.RETIRED
        },
        AssetStatus.RETIRED: {
            AssetStatus.DISPOSED
        },
        AssetStatus.DISPOSED: set()  # Terminal state
    }

    @classmethod
    def validate_transition(cls, current_state: AssetStatus, target_state: AssetStatus):
        if target_state not in cls.ALLOWED_TRANSITIONS.get(current_state, set()):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid state transition from {current_state.value} to {target_state.value}"
            )