import uuid
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Resala Platform.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)

    # First and last name do not cover name patterns around the globe
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    username = None  # type: ignore[assignment]

    auc_id = models.CharField(_("AUC ID"), max_length=20, unique=True, blank=False)
    auc_email = models.EmailField(_("AUC email"), unique=True)
    committee_role = models.ForeignKey(
        "committees.CommitteeRole",
        verbose_name=_("Committee Role"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )

    USERNAME_FIELD = "auc_email"
    REQUIRED_FIELDS = ["auc_id"]

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})
