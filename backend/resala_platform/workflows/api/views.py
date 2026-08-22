from rest_framework import viewsets

from resala_platform.workflows.models import Workflow
from resala_platform.workflows.models import WorkflowState
from resala_platform.workflows.models import WorkflowTransition
from resala_platform.workflows.models import WorkflowTransitionAction
from resala_platform.workflows.models import WorkflowTransitionRule
from resala_platform.workflows.permissions import IsPresidentialOfficeLeader
from resala_platform.workflows.serializers import WorkflowSerializer
from resala_platform.workflows.serializers import WorkflowStateSerializer
from resala_platform.workflows.serializers import WorkflowTransitionRuleSerializer
from resala_platform.workflows.serializers import WorkflowTransitionsActionSerializer
from resala_platform.workflows.serializers import WorkflowTransitionSerializer


class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    permission_classes = [IsPresidentialOfficeLeader]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class WorkflowStateViewSet(viewsets.ModelViewSet):
    queryset = WorkflowState.objects.all()
    serializer_class = WorkflowStateSerializer
    permission_classes = [IsPresidentialOfficeLeader]


class WorkflowTransitionViewSet(viewsets.ModelViewSet):
    queryset = WorkflowTransition.objects.all()
    serializer_class = WorkflowTransitionSerializer
    permission_classes = [IsPresidentialOfficeLeader]


class WorkflowTransitionRuleViewset(viewsets.ModelViewSet):
    queryset = WorkflowTransitionRule.objects.all()
    serializer_class = WorkflowTransitionRuleSerializer
    permission_classes = [IsPresidentialOfficeLeader]


class WorkflowTransitionActionViewSet(viewsets.ModelViewSet):
    queryset = WorkflowTransitionAction.objects.all()
    serializer_class = WorkflowTransitionsActionSerializer
    permission_classes = [IsPresidentialOfficeLeader]
