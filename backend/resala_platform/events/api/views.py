from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_fsm import TransitionNotAllowed

from resala_platform.events.models import Event, Budget, Request, RequestEscalation
from .serializers import (
    EventSerializer,
    BudgetSerializer,
    RequestSerializer,
    RequestEscalationSerializer,
)

class BaseWorkflowViewSet(viewsets.ModelViewSet):
    """
    A base ViewSet to handle repetitive FSM transition logic.
    """
    def perform_transition(self, transition_name):
        instance = self.get_object()
        try:
            # Dynamically fetch and call the FSM transition method
            transition_method = getattr(instance, transition_name)
            transition_method()
            instance.save()
            
            # Note: In a production app, you would also create the 
            # StateTransition log record here.
            
            # Determine which state field was updated to return dynamically
            state_field = "status" if hasattr(instance, "status") else "current_state"
            new_state = getattr(instance, state_field)
            
            return Response(
                {"status": "Transition successful", "new_state": new_state},
                status=status.HTTP_200_OK
            )
        except TransitionNotAllowed:
            return Response(
                {"error": f"Transition '{transition_name}' not allowed from current state."},
                status=status.HTTP_400_BAD_REQUEST
            )

class EventViewSet(BaseWorkflowViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @action(detail=True, methods=["post"])
    def submit_for_budget_review(self, request, pk=None):
        return self.perform_transition("submit_for_budget_review")

    @action(detail=True, methods=["post"])
    def treasurer_approve_budget(self, request, pk=None):
        return self.perform_transition("treasurer_approve_budget")

    @action(detail=True, methods=["post"])
    def treasurer_escalate_budget(self, request, pk=None):
        return self.perform_transition("treasurer_escalate_budget")

    @action(detail=True, methods=["post"])
    def president_approve_budget(self, request, pk=None):
        return self.perform_transition("president_approve_budget")

    @action(detail=True, methods=["post"])
    def reject_budget(self, request, pk=None):
        return self.perform_transition("reject_budget")

    @action(detail=True, methods=["post"])
    def revise_budget(self, request, pk=None):
        return self.perform_transition("revise_budget")

    @action(detail=True, methods=["post"])
    def turn_down_event(self, request, pk=None):
        return self.perform_transition("turn_down_event")

    @action(detail=True, methods=["post"])
    def activate_event(self, request, pk=None):
        return self.perform_transition("activate_event")

    @action(detail=True, methods=["post"])
    def complete_event(self, request, pk=None):
        return self.perform_transition("complete_event")

class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer

class RequestViewSet(BaseWorkflowViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

    @action(detail=True, methods=["post"])
    def submit_request(self, request, pk=None):
        return self.perform_transition("submit_request")

    @action(detail=True, methods=["post"])
    def begin_review(self, request, pk=None):
        return self.perform_transition("begin_review")

    @action(detail=True, methods=["post"])
    def approve_request(self, request, pk=None):
        return self.perform_transition("approve_request")

    @action(detail=True, methods=["post"])
    def reject_request(self, request, pk=None):
        return self.perform_transition("reject_request")

class RequestEscalationViewSet(BaseWorkflowViewSet):
    queryset = RequestEscalation.objects.all()
    serializer_class = RequestEscalationSerializer

    @action(detail=True, methods=["post"])
    def review_escalation(self, request, pk=None):
        return self.perform_transition("review_escalation")

    @action(detail=True, methods=["post"])
    def resolve_escalation(self, request, pk=None):
        return self.perform_transition("resolve_escalation")

    @action(detail=True, methods=["post"])
    def dismiss_escalation(self, request, pk=None):
        return self.perform_transition("dismiss_escalation")