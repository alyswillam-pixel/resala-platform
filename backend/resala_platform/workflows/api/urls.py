from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import WorkflowStateViewSet
from .views import WorkflowTransitionActionViewSet
from .views import WorkflowTransitionRuleViewset
from .views import WorkflowTransitionViewSet
from .views import WorkflowViewSet

router = DefaultRouter()

router.register("workflows", WorkflowViewSet, base_name="workflow")
router.register("workflow-states", WorkflowStateViewSet, base_name="workflow-state")
router.register(
    "workflow-transitions",
    WorkflowTransitionViewSet,
    base_name="workflow-transition",
)
router.register(
    "workflow-transition-rules",
    WorkflowTransitionRuleViewset,
    base_name="workflow-transition-rule",
)
router.register(
    "workflow-transition-actions",
    WorkflowTransitionActionViewSet,
    base_name="workflow-transition-action",
)

urlpatterns = [
    path("", include(router.urls)),
]
