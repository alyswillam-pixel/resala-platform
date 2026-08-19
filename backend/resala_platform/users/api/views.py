from django.conf import settings
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from knox.views import LogoutAllView as KnoxLogoutAllView
from knox.views import LogoutView as KnoxLogoutView
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from resala_platform.users.models import User
from resala_platform.users.tasks import send_password_setup_email

from .authentication import CookieTokenAuthentication
from .serializers import LoginSerializer
from .serializers import PasswordResetConfirmSerializer
from .serializers import PasswordResetRequestSerializer
from .serializers import UserSerializer


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class LoginView(KnoxLoginView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data["auc_email"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            return Response(
                {"detail": "Invalid AUC email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        request.user = user
        response = super().post(request, *args, **kwargs)

        # Knox returns the token in the response body
        token = response.data.pop("token")

        response.set_cookie(
            key="knox_token",
            value=token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            max_age=15 * 60,
        )

        return response


class LogoutView(KnoxLogoutView):
    authentication_classes = [CookieTokenAuthentication]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.delete_cookie("knox_token", samesite="Lax")

        return response


class LogoutAllView(KnoxLogoutAllView):
    authentication_classes = [CookieTokenAuthentication]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.delete_cookie("knox_token", samesite="Lax")

        return response


class CSRFTokenView(APIView):
    permission_classes = [AllowAny]
    authenticate_classes = []

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class RequestPasswordResetView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            auc_email__iexact=serializer.validated_data["auc_email"],
            is_active=True,
        ).first()

        if user:
            send_password_setup_email.delay(user.pk, purpose="reset")

        return Response(
            {
                "detail": "If an account exists for that email, "
                "a reset link will be sent.",
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        # Any password reset should immediately kill every previously issued
        # Knox session for this user
        AuthToken.objects.filter(user=user).delete()

        return Response(
            {"detail": "Password has been reset."},
            status=status.HTTP_200_OK,
        )
