from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from resala_platform.events.flows import EventFlow
from resala_platform.events.models import Budget
from resala_platform.events.models import Event
from resala_platform.events.models import EventStateTransition
from resala_platform.events.permissions import CanCreateEvents

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


def make_transition_action(transition_name, description):
    """Factory to generate DRF actions dynamically."""

    @extend_schema(
        summary=transition_name.replace("_", " ").title(),
        description=description,
        request=None,
        responses={
            200: OpenApiResponse(
                description="Transition successful, returns the new state.",
            ),
            400: OpenApiResponse(
                description="Transition not allowed from the current state.",
            ),
            403: OpenApiResponse(
                description="You do not have permission to perform this action.",
            ),
        },
    )
    def _action(self, request, pk=None):
        return self.perform_transition(transition_name)

    _action.__name__ = transition_name
    return action(
        detail=True,
        methods=["post"],
        url_path=transition_name,
        url_name=transition_name.replace("_", "-"),
    )(_action)


@extend_schema_view(
    list=extend_schema(
        summary="List Events",
        description="Retrieve a list of all events.",
    ),
    retrieve=extend_schema(
        summary="Retrieve Event",
        description="Get details of a specific event.",
    ),
    create=extend_schema(
        summary="Create Event",
        description=(
            "Create a new event in Draft state. You automatically become the requester."
        ),
    ),
    update=extend_schema(
        summary="Update Event",
        description="Update an event's details. Usually only allowed in Draft state.",
    ),
    partial_update=extend_schema(
        summary="Partial Update Event",
        description="Partially update an event's details.",
    ),
    destroy=extend_schema(
        summary="Delete Event",
        description="Delete an event. Allowed only for drafts or admins.",
    ),
)
class EventViewSet(BaseWorkflowViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    flow_class = EventFlow
    transition_log_model = EventStateTransition
    transition_log_fk = "event"

    def get_permissions(self):
        permissions = super().get_permissions()
        if self.action == "create":
            permissions.append(CanCreateEvents())
        return permissions

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)

    TRANSITIONS = {
        "submit_for_budget_review": "Submit a Draft event for Treasurer Review.",
        "treasurer_approve_budget": (
            "[Treasurer] Approve the budget. Event moves to Budget Approved."
        ),
        "treasurer_escalate_budget": (
            "[Treasurer] Escalate the budget to the Presidential Office."
        ),
        "president_approve_budget": (
            "[PO Leader] Approve an escalated budget. Event moves to Budget Approved."
        ),
        "reject_budget": (
            "[Treasurer/PO] Reject the budget. Event moves to Budget Rejected."
        ),
        "revise_budget": (
            "[Requester] Move a Rejected event back to Draft for revisions."
        ),
        "turn_down_event": ("[Treasurer/PO] Permanently turn down a rejected event."),
        "activate_event": (
            "[Requester] Activate the event after its budget is approved."
        ),
        "complete_event": "[Requester] Mark an Active event as Completed.",
    }

    for transition_name, description in TRANSITIONS.items():
        locals()[transition_name] = make_transition_action(transition_name, description)


@extend_schema_view(
    list=extend_schema(
        summary="List Budgets",
        description="Retrieve a list of budgets.",
    ),
    retrieve=extend_schema(
        summary="Retrieve Budget",
        description="Get details of a specific budget.",
    ),
    create=extend_schema(
        summary="Create Budget",
        description=(
            "Create a budget for your own Draft event. "
            "An event can only have one budget."
        ),
    ),
    update=extend_schema(
        summary="Update Budget",
        description=(
            "Update your budget. Allowed only while the associated "
            "event is in Draft state."
        ),
    ),
    partial_update=extend_schema(
        summary="Partial Update Budget",
        description="Partially update your budget.",
    ),
    destroy=extend_schema(summary="Delete Budget", description="Delete a budget."),
)
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
