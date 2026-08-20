from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from resala_platform.events.flows import EventFlow
from resala_platform.events.models import Budget
from resala_platform.events.models import Event
from resala_platform.events.models import EventStateTransition

from .serializers import BudgetSerializer
from .serializers import EventSerializer


class BaseWorkflowViewSet(viewsets.ModelViewSet):
    flow_class = None
    transition_log_model = None
    transition_log_fk = None

    def perform_transition(self, transition_name):
        instance = self.get_object()
        flow = self.flow_class(instance)
        transition_method = getattr(flow, transition_name)

        if not transition_method.can_proceed():
            return Response(
                {
                    "error": (
                        f"Transition '{transition_name}' not allowed "
                        "from current state."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not transition_method.has_perm(self.request.user):
            raise PermissionDenied(
                f"You do not have permission to perform '{transition_name}'.",
            )

        old_state = instance.current_state
        transition_method(by_user=self.request.user)
        instance.save()

        self.transition_log_model.objects.create(
            **{self.transition_log_fk: instance},
            from_state=old_state,
            to_state=instance.current_state,
            action=transition_name,
            actor=self.request.user,
        )

        return Response(
            {
                "status": "Transition successful",
                "new_state": instance.current_state,
            },
            status=status.HTTP_200_OK,
        )


def make_transition_action(transition_name):
    """Factory to generate DRF actions dynamically."""

    def _action(self, request, pk=None):
        return self.perform_transition(transition_name)

    _action.__name__ = transition_name
    return action(
        detail=True,
        methods=["post"],
        url_path=transition_name,
        url_name=transition_name.replace("_", "-"),
    )(_action)


class EventViewSet(BaseWorkflowViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    flow_class = EventFlow
    transition_log_model = EventStateTransition
    transition_log_fk = "event"

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)

    TRANSITIONS = [
        "submit_for_budget_review",
        "treasurer_approve_budget",
        "treasurer_escalate_budget",
        "president_approve_budget",
        "reject_budget",
        "revise_budget",
        "turn_down_event",
        "activate_event",
        "complete_event",
    ]

    for transition in TRANSITIONS:
        locals()[transition] = make_transition_action(transition)


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer

    def perform_create(self, serializer):
        event = serializer.validated_data["event"]
        if event.requester != self.request.user:
            raise PermissionDenied("You can only create a budget for your own events.")
        if hasattr(event, "budget"):
            raise PermissionDenied("This event already has a budget")
        serializer.save()

    def perform_update(self, serializer):
        event = serializer.instance.event
        if event.requester != self.request.user or event.current_state != "Draft":
            raise PermissionDenied(
                "You can only modify budgets for your own draft events.",
            )
        serializer.save()
