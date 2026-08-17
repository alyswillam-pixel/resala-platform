from django.conf import settings
from django.urls import path
from knox import views as knox_views

from rest_framework.routers import DefaultRouter, SimpleRouter

from resala_platform.users.api.views import UserViewSet, LoginView

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register("users", UserViewSet)

app_name = "api"

urlpatterns = router.urls + [
    path("auth/login/", LoginView.as_view(), name="knox_login"),
    path("auth/logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path("auth/logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"),
]
