from viewflow import fsm

from .models import Event
from .models import EventState
from .permissions import is_event_requester
from .permissions import is_po_leader
from .permissions import is_treasurer
from .permissions import is_treasurer_or_po_leader


class EventFlow:
    """
    Wraps an Event instance and encodes the Event/Budget approval workflow. The
    State lives as a field on the model; however, this class defines the
    transition graph and per-transition authorization only.
    """

    state = fsm.State(EventState, default=EventState.DRAFT)

    def __init__(self, event: Event):
        self.event = event

    @state.getter()
    def _get_state(self):
        return self.event.current_state

    @state.setter()
    def _set_state(self, value):
        self.event.current_state = value

    @state.transition(
        source=EventState.DRAFT,
        target=EventState.PENDING_TREASURER_REVIEW,
        permission=is_event_requester,
    )
    def submit_for_budget_review(self, by_user=None):
        if hasattr(self.event, "budget"):
            self.event.budget.status = EventState.PENDING_TREASURER_REVIEW
            self.event.budget.save()

    @state.transition(
        source=EventState.PENDING_TREASURER_REVIEW,
        target=EventState.BUDGET_APPROVED,
        permission=is_treasurer,
    )
    def treasurer_approve_budget(self, by_user=None):
        self._approve_budget(by_user)

    @state.transition(
        source=EventState.PENDING_TREASURER_REVIEW,
        target=EventState.PENDING_PRESIDENTIAL_REVIEW,
        permission=is_treasurer,
    )
    def treasurer_escalate_budget(self, by_user=None):
        if hasattr(self.event, "budget"):
            self.event.budget.status = EventState.PENDING_PRESIDENTIAL_REVIEW
            self.event.budget.save()

    @state.transition(
        source=EventState.PENDING_PRESIDENTIAL_REVIEW,
        target=EventState.BUDGET_APPROVED,
        permission=is_po_leader,
    )
    def president_approve_budget(self, by_user=None):
        self._approve_budget(by_user)

    @state.transition(
        source={
            EventState.PENDING_TREASURER_REVIEW,
            EventState.PENDING_TREASURER_REVIEW,
        },
        target=EventState.BUDGET_REJECTED,
        permission=is_treasurer_or_po_leader,
    )
    def reject_budget(self, by_user=None):
        if hasattr(self.event, "budget"):
            self.event.budget.status = "Rejected"
            self.event.budget.save()

    @state.transition(
        source=EventState.BUDGET_REJECTED,
        target=EventState.DRAFT,
        permission=is_event_requester,
    )
    def revise_budget(self, by_user=None):
        if hasattr(self.event, "budget"):
            self.event.budget.status = "Pending"
            self.event.budget.approved_by = None
            self.event.budget.save()

    @state.transition(
        source=EventState.BUDGET_REJECTED,
        target=EventState.TURNED_DOWN,
        permission=is_treasurer_or_po_leader,
    )
    def turn_down_event(self, by_user=None):
        pass

    @state.transition(
        source=EventState.BUDGET_APPROVED,
        target=EventState.ACTIVE,
        permission=is_event_requester,
    )
    def activate_event(self, by_user=None):
        pass

    @state.transition(
        source=EventState.ACTIVE,
        target=EventState.COMPLETED,
        permission=is_event_requester,
    )
    def complete_event(self, by_user=None):
        pass

    def _approve_budget(self, by_user):
        if hasattr(self.event, "budget"):
            self.event.budget.status = "Approved"
            self.event.budget.approved_by = by_user
            self.event.budget.save()
