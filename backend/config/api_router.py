from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from resala_platform.users.api.views import CSRFTokenView
from resala_platform.users.api.views import LoginView
from resala_platform.users.api.views import LogoutAllView
from resala_platform.users.api.views import LogoutView
from resala_platform.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register("users", UserViewSet)

app_name = "api"

urlpatterns = router.urls + [
    path("auth/login/", LoginView.as_view(), name="knox_login"),
    path("auth/logout/", LogoutView.as_view(), name="knox_logout"),
    path("auth/logoutall/", LogoutAllView.as_view(), name="knox_logoutall"),
    path("auth/csrf/", CSRFTokenView.as_view(), name="csrf_token"),
]
