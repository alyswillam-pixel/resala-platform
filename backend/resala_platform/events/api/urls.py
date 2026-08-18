from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    EventViewSet,
    BudgetViewSet,
    RequestViewSet,
    RequestEscalationViewSet,
)

app_name = "events_api"

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")
router.register(r"budgets", BudgetViewSet, basename="budget")
router.register(r"requests", RequestViewSet, basename="request")
router.register(r"escalations", RequestEscalationViewSet, basename="escalation")

urlpatterns = [
    path("", include(router.urls)),
]