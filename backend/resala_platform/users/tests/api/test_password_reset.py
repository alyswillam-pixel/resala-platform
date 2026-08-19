from http import HTTPStatus
from unittest import mock

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from knox.models import AuthToken
from rest_framework.test import APIClient

from resala_platform.users.models import User
from resala_platform.users.tasks import send_password_setup_email
from resala_platform.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

OLD_PASSWORD = "OldPassword123!"
NEW_PASSWORD = "BrandNewDaySpideyPassword456!"
NONEXISTENT_EMAIL = "mr.nobody@aucegypt.edu"


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user() -> User:
    return UserFactory(password=OLD_PASSWORD)


@pytest.fixture
def reset_tokens(user) -> tuple[str, str]:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token


class TestRequestPasswordReset:
    def test_existing_user_gets_generic_success_response(self, api_client, user):
        response = api_client.post(
            reverse("api:password_reset_request"),
            {"auc_email": user.auc_email},
        )
        assert response.status_code == HTTPStatus.OK

    def test_nonexistent_user_gets_identical_response(self, api_client, user):
        real = api_client.post(
            reverse("api:password_reset_request"),
            {"auc_email": user.auc_email},
        )
        fake = api_client.post(
            reverse("api:password_reset_request"),
            {"auc_email": NONEXISTENT_EMAIL},
        )
        assert real.status_code == fake.status_code == HTTPStatus.OK
        assert real.data == fake.data

    def test_existing_active_user_triggers_email_task(self, api_client, user):
        with mock.patch.object(send_password_setup_email, "delay") as delay:
            api_client.post(
                reverse("api:password_reset_request"),
                {"auc_email": user.auc_email},
            )
        delay.assert_called_once_with(user.pk, purpose="reset")

    def test_nonexistent_user_does_not_trigger_email_task(self, api_client):
        with mock.patch.object(send_password_setup_email, "delay") as delay:
            api_client.post(
                reverse("api:password_reset_request"),
                {"auc_email": NONEXISTENT_EMAIL},
            )
        delay.assert_not_called()

    def test_inactive_user_does_not_trigger_email_task(self, api_client, user):
        user.is_active = False
        user.save(update_fields=["is_active"])

        with mock.patch.object(send_password_setup_email, "delay") as delay:
            response = api_client.post(
                reverse("api:password_reset_request"),
                {"auc_email": user.auc_email},
            )
        delay.assert_not_called()
        assert response.status_code == HTTPStatus.OK

    def test_missing_email_field_is_a_validation_error(self, api_client):
        response = api_client.post(reverse("api:password_reset_request"), {})
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_endpoint_requires_no_authentication(self, api_client, user):
        response = api_client.post(
            reverse("api:password_reset_request"),
            {"auc_email": user.auc_email},
        )
        assert response.status_code == HTTPStatus.OK


class TestPasswordResetConfirm:
    def test_valid_token_sets_new_password(self, api_client, user, reset_tokens):
        uid, token = reset_tokens
        response = api_client.post(
            reverse("api:password_reset_confirm"),
            {
                "uid": uid,
                "token": token,
                "new_password": NEW_PASSWORD,
            },
        )
        assert response.status_code == HTTPStatus.OK

        user.refresh_from_db()
        assert user.check_password(NEW_PASSWORD)
        assert not user.check_password(OLD_PASSWORD)

    def test_reused_token_is_rejected(self, api_client, user, reset_tokens):
        uid, token = reset_tokens
        first = api_client.post(
            reverse("api:password_reset_confirm"),
            {
                "uid": uid,
                "token": token,
                "new_password": NEW_PASSWORD,
            },
        )
        assert first.status_code == HTTPStatus.OK

        second = api_client.post(
            reverse("api:password_reset_confirm"),
            {
                "uid": uid,
                "token": token,
                "new_password": "SomethingElse789ItisaPun!",
            },
        )
        assert second.status_code == HTTPStatus.BAD_REQUEST

    def test_garbage_token_is_rejected(self, api_client, user, reset_tokens):
        uid, _ = reset_tokens
        response = api_client.post(
            reverse("api:password_reset_confirm"),
            {
                "uid": uid,
                "token": "a-red-herring-token",
                "new_password": NEW_PASSWORD,
            },
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST

        user.refresh_from_db()
        assert user.check_password(OLD_PASSWORD)

    def test_garbage_uid_is_rejected(self, api_client, user, reset_tokens):
        _, token = reset_tokens
        response = api_client.post(
            reverse("api:password_reset_confirm"),
            {
                "uid": "mystique-uid",
                "token": token,
                "new_password": NEW_PASSWORD,
            },
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_uid_for_nonexistent_user_is_rejected(self, api_client, reset_tokens):
        _, token = reset_tokens
        fake_uid = urlsafe_base64_encode(
            force_bytes("00000000-0000-0000-0000-000000000000"),
        )
        response = api_client.post(
            reverse("api:password_reset_confirm"),
            {
                "uid": fake_uid,
                "token": token,
                "new_password": NEW_PASSWORD,
            },
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_weak_password_is_rejected_by_validator(
        self,
        api_client,
        user,
        reset_tokens,
    ):
        uid, token = reset_tokens
        response = api_client.post(
            reverse("api:password_reset_confirm"),
            {
                "uid": uid,
                "token": token,
                "new_password": "123456",
            },
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "new_password" in response.data

        user.refresh_from_db()
        assert user.check_password(OLD_PASSWORD)

    def test_successful_reset_revokes_all_existing_knox_sessions(
        self,
        api_client,
        user,
        reset_tokens,
    ):
        AuthToken.objects.create(user)
        AuthToken.objects.create(user)
        assert AuthToken.objects.filter(user=user).count() == 2

        uid, token = reset_tokens
        response = api_client.post(
            reverse("api:password_reset_confirm"),
            {
                "uid": uid,
                "token": token,
                "new_password": NEW_PASSWORD,
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert AuthToken.objects.filter(user=user).count() == 0

    def test_endpoint_requires_no_authentication(self, api_client, user, reset_tokens):
        uid, token = reset_tokens
        response = api_client.post(
            reverse("api:password_reset_confirm"),
            {
                "uid": uid,
                "token": token,
                "new_password": NEW_PASSWORD,
            },
        )
        assert response.status_code == HTTPStatus.OK


class TestSendPasswordSetupEmailTask:
    def test_reset_email_contains_working_link_and_reaches_auc_email(
        self,
        user,
        settings,
    ):
        settings.FRONTEND_URL = "https://resala.example"
        mail.outbox = []

        send_password_setup_email(user.pk, purpose="reset")

        assert len(mail.outbox) == 1
        sent = mail.outbox[0]
        assert sent.to == [user.auc_email]
        assert "https://resala.example/reset-password" in sent.body
        assert "uid=" in sent.body
        assert "token=" in sent.body

    def test_new_account_email_uses_distinct_subject(self, user, settings):
        settings.FRONTEND_URL = "https://resala.example"
        mail.outbox = []

        send_password_setup_email(user.pk, purpose="new_account")

        assert len(mail.outbox) == 1
        assert "set your password" in mail.outbox[0].subject.lower()

    def test_deleted_user_id_does_not_raise(self, user):
        deleted_pk = user.pk
        user.delete()
        mail.outbox = []
        send_password_setup_email(deleted_pk, purpose="reset")
        assert len(mail.outbox) == 0
