from __future__ import annotations

from src.domain.entities.maintenance import MaintenanceRequest, MaintenanceStatus
from src.domain.exceptions.domain_exceptions import InvalidMaintenanceTransitionError

# PENDING -> APPROVED, REJECTED
# APPROVED -> TECHNICIAN_ASSIGNED
# TECHNICIAN_ASSIGNED -> IN_PROGRESS
# IN_PROGRESS -> RESOLVED
# REJECTED, RESOLVED are terminal.
_ALLOWED_TRANSITIONS: dict[MaintenanceStatus, frozenset[MaintenanceStatus]] = {
    MaintenanceStatus.PENDING: frozenset({MaintenanceStatus.APPROVED, MaintenanceStatus.REJECTED}),
    MaintenanceStatus.APPROVED: frozenset({MaintenanceStatus.TECHNICIAN_ASSIGNED}),
    MaintenanceStatus.TECHNICIAN_ASSIGNED: frozenset({MaintenanceStatus.IN_PROGRESS}),
    MaintenanceStatus.IN_PROGRESS: frozenset({MaintenanceStatus.RESOLVED}),
    MaintenanceStatus.REJECTED: frozenset(),
    MaintenanceStatus.RESOLVED: frozenset(),
}


class MaintenanceStateMachine:
    """
    Sole authority on legal maintenance-workflow moves — same role as
    AssetStateMachine plays for the asset lifecycle. MaintenanceService
    calls `transition()` rather than mutating `.status` directly; the
    resulting asset-status side effects (APPROVED -> asset UNDER_MAINTENANCE,
    RESOLVED -> asset AVAILABLE) are orchestrated by MaintenanceService using
    AssetStateMachine separately, so this class has zero knowledge of Asset
    at all — one-directional dependency, no cycle.
    """

    @staticmethod
    def can_transition(from_state: MaintenanceStatus, to_state: MaintenanceStatus) -> bool:
        if from_state == to_state:
            return False
        return to_state in _ALLOWED_TRANSITIONS.get(from_state, frozenset())

    @staticmethod
    def transition(request: MaintenanceRequest, to_state: MaintenanceStatus) -> MaintenanceRequest:
        if not MaintenanceStateMachine.can_transition(request.status, to_state):
            raise InvalidMaintenanceTransitionError(from_state=request.status.value, to_state=to_state.value)
        request.apply_transition(to_state)
        return request

    @staticmethod
    def legal_next_states(from_state: MaintenanceStatus) -> frozenset[MaintenanceStatus]:
        return _ALLOWED_TRANSITIONS.get(from_state, frozenset())
