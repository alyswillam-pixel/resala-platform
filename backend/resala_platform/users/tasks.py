from celery import shared_task

from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from resala_platform.users.models import User


@shared_task
def send_new_user_credentials_email(user_pk, base_url):
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return

    uid = user_pk_to_url_str(user)
    token = default_token_generator.make_token(user)

    reset_url = base_url + reverse(
        "account_reset_password_from_key",
        kwargs={"uidb36": uid, "key": token}
    )

    subject = "Welcome to Resala — Setup Your Account"
    msg = (
        f"Hello,\n\n"
        f"An account has been created for you on the Resala Platform.\n"
        f"Your AUC Email: {user.auc_email}\n\n"
        f"To set your password and access your account, please click the link below:\n"
        f"{reset_url}\n\n"
        f"This link will expire in a few days. If you need a new link, you can use the "
        f"'Forgot Password' page on the site."
    )

    send_mail(
        subject=subject,
        message=msg,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.auc_email],
        fail_silently=False,
    )
