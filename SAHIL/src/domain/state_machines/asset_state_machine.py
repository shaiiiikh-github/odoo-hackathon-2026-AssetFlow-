from __future__ import annotations

from src.domain.entities.asset import Asset, AssetStatus
from src.domain.exceptions.domain_exceptions import InvalidStateTransitionError

# Adjacency map of legal transitions. This is intentionally the ONLY place
# in the codebase that knows the asset lifecycle graph — services call
# `AssetStateMachine.transition(...)`, never `asset.status = X` directly.
#
#   AVAILABLE  <-> UNDER_MAINTENANCE
#   AVAILABLE   -> ALLOCATED, RESERVED, LOST, RETIRED
#   ALLOCATED   -> AVAILABLE, UNDER_MAINTENANCE, LOST      (return / repair-while-held / reported lost)
#   RESERVED    -> AVAILABLE, ALLOCATED                    (booking cancelled / booking converted to allocation)
#   UNDER_MAINTENANCE -> AVAILABLE, LOST, RETIRED           (resolved / found unrepairable / written off)
#   LOST        -> AVAILABLE, RETIRED, DISPOSED             (recovered / written off)
#   RETIRED     -> DISPOSED
#   DISPOSED    -> (terminal, no outgoing transitions)
_ALLOWED_TRANSITIONS: dict[AssetStatus, frozenset[AssetStatus]] = {
    AssetStatus.AVAILABLE: frozenset(
        {AssetStatus.ALLOCATED, AssetStatus.RESERVED, AssetStatus.UNDER_MAINTENANCE, AssetStatus.LOST, AssetStatus.RETIRED}
    ),
    AssetStatus.ALLOCATED: frozenset({AssetStatus.AVAILABLE, AssetStatus.UNDER_MAINTENANCE, AssetStatus.LOST}),
    AssetStatus.RESERVED: frozenset({AssetStatus.AVAILABLE, AssetStatus.ALLOCATED}),
    AssetStatus.UNDER_MAINTENANCE: frozenset({AssetStatus.AVAILABLE, AssetStatus.LOST, AssetStatus.RETIRED}),
    AssetStatus.LOST: frozenset({AssetStatus.AVAILABLE, AssetStatus.RETIRED, AssetStatus.DISPOSED}),
    AssetStatus.RETIRED: frozenset({AssetStatus.DISPOSED}),
    AssetStatus.DISPOSED: frozenset(),  # terminal — e.g. DISPOSED -> ALLOCATED is always rejected
}


class AssetStateMachine:
    @staticmethod
    def can_transition(from_state: AssetStatus, to_state: AssetStatus) -> bool:
        if from_state == to_state:
            return False  # no-op transitions are rejected explicitly, not silently accepted
        return to_state in _ALLOWED_TRANSITIONS.get(from_state, frozenset())

    @staticmethod
    def transition(asset: Asset, to_state: AssetStatus) -> Asset:
        """
        Validates and applies a transition in place, returning the same
        asset instance for chaining. Raises InvalidStateTransitionError
        (mapped to HTTP 400) if the move is illegal — callers must not
        catch-and-ignore this; it is the mechanism that stops
        DISPOSED -> ALLOCATED, RETIRED -> AVAILABLE, etc.
        """
        if not AssetStateMachine.can_transition(asset.status, to_state):
            raise InvalidStateTransitionError(from_state=asset.status.value, to_state=to_state.value)
        asset.apply_transition(to_state)
        return asset

    @staticmethod
    def legal_next_states(from_state: AssetStatus) -> frozenset[AssetStatus]:
        """Exposed for the API layer to tell the UI which transitions are currently offerable."""
        return _ALLOWED_TRANSITIONS.get(from_state, frozenset())
