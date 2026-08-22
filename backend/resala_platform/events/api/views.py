from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from resala_platform.events.models import Budget
from resala_platform.events.models import Event
from resala_platform.events.permissions import CanCreatedEvents
from resala_platform.workflows.engine import InvalidTransitionError
from resala_platform.workflows.engine import UnAuthorizedTransitionError
from resala_platform.workflows.engine import Workflow
from resala_platform.workflows.engine import WorkflowEngine
from resala_platform.workflows.engine import WorkflowInstance
from resala_platform.workflows.engine import WorkflowService
from resala_platform.workflows.engine import WorkflowTransition

from .serializers import BudgetSerializer
from .serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        permissions = super().get_permissions()

        if self.action == "create":
            permissions.append(CanCreatedEvents())

        return permissions

    def perform_create(self, serializer):
        event = serializer.save(requester=self.request.user)
        workflow = Workflow.objects.filter(
            content_type__app_label="events",
            content_type__model="event",
            is_active=True,
        ).first()

        if workflow:
            WorkflowService.start(obj=event, workflow=workflow)

    @extend_schema(
        summary="Last Available Workflow Transitions",
        description=(
            "Return the workflow transitions that the current user may execute"
            "for this event."
        ),
        responses={200: OpenApiResponse(description="Available transitions.")},
    )
    @action(detail=True, methods=["get"], url_path="workflow/transitions")
    def workflow_transitions(self, request, pk=None):
        event = self.get_object()

        try:
            instance = event.workflow_instance.get()
        except WorkflowInstance.DoesNotExist:
            return Response(
                {"error": "This event has no workflow instance."},
                status=status.HTTP_404_NOT_FOUND,
            )

        engine = WorkflowEngine(instance)
        transitions = engine.available_transitions(request.user)

        return Response(
            [
                {
                    "id": str(transition.id),
                    "name": transition.name,
                    "description": transition.description,
                    "target_state": transition.target.name,
                }
                for transition in transitions
            ],
        )

    @extend_schema(
        summary="Execute Workflow Transition",
        description=("Execute a configured workflow transition for this event."),
        request=None,
        responses={
            200: OpenApiResponse(
                description="Transition successfully executed.",
            ),
            400: OpenApiResponse(
                description="Transition is not available.",
            ),
            403: OpenApiResponse(
                description="User is not authorized.",
            ),
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path=r"workflow/transitions/(?P<transition_id>[^/.]+)",
    )
    def execute_transition(self, request, pk=None, transition_id=None):
        event = self.get_object()

        try:
            instance = event.workflow_instance.get()
        except WorkflowInstance.DoesNotExist:
            return Response(
                {"error": "This event has no workflow instance."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            transition = WorkflowTransition.objects.get(pk=transition_id)
        except WorkflowTransition.DoesNotExist:
            return Response(
                {"error": "Transition not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        engine = WorkflowEngine(instance)

        try:
            instance = engine.execute(
                transition=transition,
                user=request.user,
                note=request.data.get("note", ""),
            )
        except InvalidTransitionError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except UnAuthorizedTransitionError as exc:
            raise PermissionDenied(str(exc)) from exc

        return Response(
            {
                "status": "Transition successful",
                "state": instance.current_state.name,
            },
            status=status.HTTP_200_OK,
        )


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
        description="Update a budget.",
    ),
    partial_update=extend_schema(
        summary="Partial Update Budget",
        description="Partially update a budget.",
    ),
    destroy=extend_schema(
        summary="Delete Budget",
        description="Delete a budget.",
    ),
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

        if event.requester != self.request.user:
            raise PermissionDenied("You can only modify your own budgets.")

        serializer.save()
