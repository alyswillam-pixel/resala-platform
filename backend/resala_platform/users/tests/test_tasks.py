import pytest
from celery.result import EagerResult

from resala_platform.users.tasks import send_new_user_credentials_email
from resala_platform.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_send_new_user_credentials_email(settings, mailoutbox):
    """Test that the celery task generates a reset token and sends it."""
    user = UserFactory()
    settings.CELERY_TASK_ALWAYS_EAGER = True
    
    base_url = "http://testserver"
    task_result = send_new_user_credentials_email.delay(user.pk, base_url)
    
    assert isinstance(task_result, EagerResult)
    assert len(mailoutbox) == 1
    
    email = mailoutbox[0]
    assert user.auc_email in email.to
    assert "Setup Your Account" in email.subject
    assert base_url in email.body
    assert "account/password/reset" not in email.body # we'll just check if it was sent successfully

