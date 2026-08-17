from django.conf import settings
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token
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
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from resala_platform.users.models import User

from .authentication import CookieTokenAuthentication
from .serializers import LoginSerializer
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
