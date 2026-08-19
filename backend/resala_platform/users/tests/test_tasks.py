import pytest
from celery.result import EagerResult

from resala_platform.users.tasks import send_password_setup_email
from resala_platform.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_send_new_user_credentials_email(settings, mailoutbox):
    """Test that the celery task generates a reset token and sends it."""
    user = UserFactory()
    settings.CELERY_TASK_ALWAYS_EAGER = True

    settings.FRONTEND_URL = "http://testserver"
    task_result = send_password_setup_email.delay(user.pk, purpose="new_account")

    assert isinstance(task_result, EagerResult)
    assert len(mailoutbox) == 1

    email = mailoutbox[0]
    assert user.auc_email in email.to
    assert "Welcome to Resala Platform — Set Your Password" in email.subject
    assert settings.FRONTEND_URL in email.body
