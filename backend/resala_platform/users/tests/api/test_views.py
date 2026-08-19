from __future__ import annotations

from http import HTTPStatus

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from resala_platform.users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        auc_email="other@aucegypt.edu",
        auc_id="900245558",
        password="TestPassword123!",
        name="Other User",
    )


class TestUserViewSet:
    def test_user_me_endpoint_returns_current_user(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.get(reverse("api:user-me"))

        assert response.status_code == HTTPStatus.OK

    def test_user_cannot_list_other_users(self, api_client, user, other_user):
        api_client.force_authenticate(user=user)
        response = api_client.get(reverse("api:user-list"))

        assert response.status_code == HTTPStatus.OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == user.name

    def test_user_cannot_retrieve_other_user_profile(
        self,
        api_client,
        user,
        other_user,
    ):
        api_client.force_authenticate(user=user)
        url = reverse("api:user-detail", kwargs={"pk": other_user.pk})
        response = api_client.get(url)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_unauthenticated_requests_are_rejected(self, api_client):
        response = api_client.get(reverse("api:user-me"))
        assert response.status_code == HTTPStatus.UNAUTHORIZED
