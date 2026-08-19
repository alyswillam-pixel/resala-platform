from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_fsm import TransitionNotAllowed, has_transition_perm, can_proceed

from resala_platform.events.models import Event, Budget, EventStateTransition
from .serializers import EventSerializer, BudgetSerializer


class BaseWorkflowViewSet(viewsets.ModelViewSet):
    """
    A base ViewSet to handle repetitive FSM transition logic, authorization,
    and audit logging.
    """
    def perform_transition(self, transition_name):
        instance = self.get_object()
        try:
            transition_method = getattr(instance, transition_name)
            
            # 1. Check if transition is valid for the current state first (returns 400)
            if not can_proceed(transition_method):
                return Response(
                    {"error": f"Transition '{transition_name}' not allowed from current state."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 2. Enforce Authorization (returns 403)
            if not has_transition_perm(transition_method, self.request.user):
                return Response(
                    {"error": "You do not have permission to perform this state transition."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            old_state = instance.current_state
            
            # 3. Execute transition (passing the user so the Budget model can log the approver)
            try:
                transition_method(by_user=self.request.user)
            except TypeError:
                transition_method()
            instance.save()
            new_state = instance.current_state
            
            # 4. Create the StateTransition log record
            EventStateTransition.objects.create(
                event=instance,
                from_state=old_state,
                to_state=new_state,
                action=transition_name,
                actor=self.request.user
            )
            
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
    
    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)

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
    """
    Exposes full CRUD, but strictly isolated so users can only touch 
    budgets linked to their own Draft events.
    """
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer

    def perform_create(self, serializer):
        event = serializer.validated_data['event']
        if event.requester != self.request.user:
            raise PermissionDenied("You can only create a budget for your own events.")
        if hasattr(event, 'budget'):
            raise PermissionDenied("This event already has a budget.")
        serializer.save()

    def perform_update(self, serializer):
        event = serializer.instance.event
        if event.requester != self.request.user or event.current_state != 'Draft':
            raise PermissionDenied("You can only modify budgets for your own draft events.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.event.requester != self.request.user or instance.event.current_state != 'Draft':
            raise PermissionDenied("You can only delete budgets for your own draft events.")
        instance.delete()