from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from resala_platform.users.api.views import CSRFTokenView
from resala_platform.users.api.views import LoginView
from resala_platform.users.api.views import LogoutAllView
from resala_platform.users.api.views import LogoutView
from resala_platform.users.api.views import UserViewSet
from resala_platform.events.api.views import (
    EventViewSet,
    BudgetViewSet,
    RequestViewSet,
    RequestEscalationViewSet,
)

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# Registering all API endpoints
router.register("users", UserViewSet)
router.register("events", EventViewSet, basename="event")
router.register("budgets", BudgetViewSet, basename="budget")
router.register("requests", RequestViewSet, basename="request")
router.register("escalations", RequestEscalationViewSet, basename="escalation")

app_name = "api"

urlpatterns = [
    *router.urls,
    path("auth/login/", LoginView.as_view(), name="knox_login"),
    path("auth/logout/", LogoutView.as_view(), name="knox_logout"),
    path("auth/logoutall/", LogoutAllView.as_view(), name="knox_logoutall"),
    path("auth/csrf/", CSRFTokenView.as_view(), name="csrf_token"),
]