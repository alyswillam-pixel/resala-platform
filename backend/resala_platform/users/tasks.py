from celery import shared_task
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from resala_platform.users.models import User

_TEMPLATES = {
    "new_account": (
        "users/email/new_account_setup.txt",
        "Welcome to Resala Platform — Set Your Password",
    ),
    "reset": ("users/email/password_reset.txt", "Reset your Resala Platform password"),
}


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_password_setup_email(self, user_id, purpose="new_account"):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uidb64}&token={token}"
    template, subject = _TEMPLATES.get(purpose, _TEMPLATES["reset"])
    message = render_to_string(template, {"user": user, "reset_url": reset_url})

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.auc_email],
        fail_silently=False,
    )
