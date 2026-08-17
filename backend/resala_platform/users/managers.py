import re
from typing import TYPE_CHECKING

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.utils import timezone

if TYPE_CHECKING:
    from .models import User  # noqa: F401


AUC_ID_PATTERN = re.compile(r"^900(\d{2})(\d{4})$")


class UserManager(DjangoUserManager["User"]):
    """Custom manager for the User model."""

    def _create_user(
        self,
        auc_email: str,
        auc_id: str,
        password: str | None,
        **extra_fields,
    ):
        """
        Create and save a user with the given email and password.
        """
        if not auc_email:
            msg = "The given AUC email must be set"
            raise ValueError(msg)
        auc_email = self.normalize_email(auc_email)
        self._validate_auc_email(auc_email)
        self._validate_auc_id(auc_id)

        user = self.model(auc_email=auc_email, auc_id=auc_id, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        auc_email: str,
        auc_id: str,
        password: str | None = None,
        **extra_fields,
    ):  # type: ignore[override]
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(
            auc_email=auc_email,
            auc_id=auc_id,
            password=password,
            **extra_fields,
        )

    def create_superuser(
        self,
        auc_email: str,
        auc_id: str,
        password: str | None = None,
        **extra_fields,
    ):  # type: ignore[override]
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            msg = "Superuser must have is_staff=True."
            raise ValueError(msg)
        if extra_fields.get("is_superuser") is not True:
            msg = "Superuser must have is_superuser=True."
            raise ValueError(msg)

        return self._create_user(
            auc_email=auc_email,
            auc_id=auc_id,
            password=password,
            **extra_fields,
        )

    @staticmethod
    def _validate_auc_email(auc_email: str) -> None:
        if not auc_email.lower().endswith("@aucegypt.edu"):
            msg = "AUC email must end with @aucegypt.edu"
            raise ValueError(msg)

    @staticmethod
    def _validate_auc_id(auc_id: str) -> None:
        """
        AUC ID format: 900<YY><NNNN> — 9 digits total
        - Always starts with "900"
        - YY is the two-digit year the ID was issued in
        - NNNN is a 4-digit sequence number

        The year portion cannot be later than the current year.
        """
        if not auc_id:
            msg = "AUC ID must not be empty"
            raise ValueError(msg)

        match = AUC_ID_PATTERN.fullmatch(str(auc_id))
        if not match:
            msg = "AUC ID must be in the format 900<YY><NNNN> (9 digits total)"
            raise ValueError(msg)

        issued_year_two_digit = int(match.group(1))
        current_year_two_digit = timezone.now().year % 100
        if issued_year_two_digit > current_year_two_digit:
            msg = "AUC ID year cannot be in the future"
            raise ValueError(msg)
