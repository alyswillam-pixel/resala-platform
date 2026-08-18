from datetime import timedelta

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from resala_platform.users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(
        auc_email="test@aucegypt.edu",
        auc_id="900245558",
        password="TestPassword123!",
        name="Test User",
    )


@pytest.fixture
def api_client():
    return APIClient()


pytestmark = pytest.mark.django_db


def test_login_sets_httponly_knox_cookie(api_client, user):
    response = api_client.post(
        reverse("api:knox_login"),
        {
            "auc_email": user.auc_email,
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert response.status_code == 200
    assert "knox_token" in response.cookies

    cookie = response.cookies["knox_token"]

    assert cookie["httponly"]
    assert cookie["samesite"] == "Lax"
    assert "token" not in response.data


def test_login_rejects_invalid_credentials(api_client, user):
    response = api_client.post(
        reverse("api:knox_login"),
        {
            "auc_email": user.auc_email,
            "password": "WrongPassword!",
        },
        format="json",
    )

    assert response.status_code == 401


def test_authenticated_request_works_with_cookie(api_client, user):
    login_response = api_client.post(
        reverse("api:knox_login"),
        {
            "auc_email": user.auc_email,
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert login_response.status_code == 200

    api_client.cookies["knox_token"] = login_response.cookies["knox_token"].value
    response = api_client.get(reverse("api:user-me"))

    assert response.status_code == 200
    assert response.data["name"] == user.name


def test_authenticated_request_fails_without_cookie(api_client):
    response = api_client.get(reverse("api:user-me"))
    assert response.status_code == 401
    assert response["WWW-Authenticate"] == "Token"


def test_logout_revokes_token(api_client, user):
    login_response = api_client.post(
        reverse("api:knox_login"),
        {
            "auc_email": user.auc_email,
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert login_response.status_code == 200

    api_client.cookies["knox_token"] = login_response.cookies["knox_token"].value
    response = api_client.post(reverse("api:knox_logout"))

    assert response.status_code == 204

    response = api_client.get(reverse("api:user-me"))

    assert response.status_code == 401
    assert response["WWW-Authenticate"] == "Token"


def test_login_cookie_has_fifteen_minute_lifetime(api_client, user):
    response = api_client.post(
        reverse("api:knox_login"),
        {
            "auc_email": user.auc_email,
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert response.status_code == 200

    cookie = response.cookies["knox_token"]

    assert cookie["max-age"] == int(timedelta(minutes=15).total_seconds())


def test_csrf_endpoint_returns_token_in_body(api_client):
    response = api_client.get(reverse("api:csrf_token"))

    assert response.status_code == 200
    assert "csrfToken" in response.data
    assert isinstance(response.data["csrfToken"], str)
    assert len(response.data["csrfToken"]) > 0


def test_csrf_endpoint_sets_cookie(api_client):
    response = api_client.get(reverse("api:csrf_token"))

    assert response.status_code == 200
    assert "csrftoken" in response.cookies

    cookie = response.cookies["csrftoken"]
    assert len(cookie.value) > 0


def test_csrf_blocks_unauthorized_post(user):
    csrf_client = APIClient(enforce_csrf_checks=True)
    login_response = csrf_client.post(
        reverse("api:knox_login"),
        {
            "auc_email": user.auc_email,
            "password": "TestPassword123!",
        },
        format="json",
    )

    csrf_client.cookies["knox_token"] = login_response.cookies["knox_token"].value
    response = csrf_client.post(reverse("api:knox_logout"))
    assert response.status_code == 403


def test_csrf_allows_post_with_valid_token(user):
    csrf_client = APIClient(enforce_csrf_checks=True)
    login_response = csrf_client.post(
        reverse("api:knox_login"),
        {
            "auc_email": user.auc_email,
            "password": "TestPassword123!",
        },
        format="json",
    )
    csrf_client.cookies["knox_token"] = login_response.cookies["knox_token"].value
    csrf_response = csrf_client.get(reverse("api:csrf_token"))
    csrf_client.cookies["csrftoken"] = csrf_response.cookies["csrftoken"].value
    response = csrf_client.post(
        reverse("api:knox_logout"),
        HTTP_X_CSRFTOKEN=csrf_response.data["csrfToken"],
    )

    assert response.status_code == 204


def test_csrf_blocks_mismatched_token(user):
    csrf_client = APIClient(enforce_csrf_checks=True)
    login_response = csrf_client.post(
        reverse("api:knox_login"),
        {
            "auc_email": user.auc_email,
            "password": "TestPassword123!",
        },
        format="json",
    )
    csrf_client.cookies["knox_token"] = login_response.cookies["knox_token"].value
    csrf_response = csrf_client.get(reverse("api:csrf_token"))
    csrf_client.cookies["csrftoken"] = csrf_response.cookies["csrftoken"].value
    response = csrf_client.post(
        reverse("api:knox_logout"),
        HTTP_X_CSRFTOKEN="not-the-real-token",
    )
    
    assert response.status_code == 403
