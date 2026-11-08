"""
Crisis state machine.

Every request moves through CrisisState values. Only transitions listed in
VALID_TRANSITIONS are allowed, and every change is logged with a timestamp
and a human-readable reason (required by the competition abstract).
"""
from datetime import datetime
from enum import Enum


class CrisisState(Enum):
    OPEN = "Open"
    PRIORITIZED = "Prioritized"
    RESOURCE_ASSIGNED = "Resource Assigned"
    IN_PROGRESS = "In Progress"
    RE_ROUTING = "Re-Routing"
    DELIVERED = "Delivered"
    RESOLVED = "Resolved"
    DELAYED = "Delayed"
    FAILED = "Failed"


S = CrisisState
VALID_TRANSITIONS = {
    S.OPEN:              {S.PRIORITIZED, S.FAILED},
    S.PRIORITIZED:       {S.RESOURCE_ASSIGNED, S.DELAYED, S.FAILED, S.RESOLVED},
    S.DELAYED:           {S.PRIORITIZED, S.FAILED},
    S.RESOURCE_ASSIGNED: {S.IN_PROGRESS, S.DELAYED, S.FAILED},
    S.IN_PROGRESS:       {S.RE_ROUTING, S.DELIVERED, S.DELAYED, S.FAILED},
    S.RE_ROUTING:        {S.IN_PROGRESS, S.DELAYED, S.FAILED},
    S.DELIVERED:         {S.RESOLVED},
    S.RESOLVED:          set(),   # terminal
    S.FAILED:            set(),   # terminal
}


class InvalidTransition(Exception):
    pass


# request_id -> list of {"state", "time", "reason"}
_history = {}


def register(request_id, reason="Request received"):
    """Put a new request into OPEN. Safe to call twice (second call is ignored)."""
    if request_id not in _history:
        _history[request_id] = [_entry(S.OPEN, reason)]


def get_state(request_id):
    history = _history.get(request_id)
    return history[-1]["state"] if history else None


def get_history(request_id):
    return list(_history.get(request_id, []))


def transition(request_id, new_state, reason):
    """Move a request to new_state if the move is valid; log it either way it succeeds."""
    current = get_state(request_id)
    if current is None:
        raise InvalidTransition(f"Request {request_id} was never registered")
    if new_state not in VALID_TRANSITIONS[current]:
        raise InvalidTransition(
            f"Request {request_id}: {current.value} -> {new_state.value} is not allowed")
    _history[request_id].append(_entry(new_state, reason))


def _entry(state, reason):
    return {"state": state, "time": datetime.now().isoformat(timespec="seconds"), "reason": reason}
