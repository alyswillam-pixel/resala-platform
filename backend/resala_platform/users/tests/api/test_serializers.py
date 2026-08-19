import pytest
from rest_framework.test import APIRequestFactory

from resala_platform.users.api.serializers import LoginSerializer
from resala_platform.users.api.serializers import UserSerializer

pytestmark = pytest.mark.django_db


class TestLoginSerializer:
    def test_login_serializer_requires_valid_email(self):
        serializer = LoginSerializer(
            data={"auc_email": "not-an-email", "password": "password"},
        )
        assert not serializer.is_valid()
        assert "auc_email" in serializer.errors

    def test_login_serializer_accepts_valid_data(self):
        serializer = LoginSerializer(
            data={"auc_email": "test@aucegypt.edu", "password": "password"},
        )
        assert serializer.is_valid()
        assert serializer.validated_data["auc_email"] == "test@aucegypt.edu"


class TestUserSerializer:
    def test_user_serializer_outputs_correct_fields(self, user):
        factory = APIRequestFactory()
        request = factory.get("/")
        serializer = UserSerializer(user, context={"request": request})
        data = serializer.data

        assert "name" in data
        assert "url" in data
        assert data["name"] == user.name
        assert "password" not in data
