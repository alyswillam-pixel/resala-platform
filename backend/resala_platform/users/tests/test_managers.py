from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command

from resala_platform.users.models import User

pytestmark = pytest.mark.django_db


class TestUserManager:
    def test_create_user(self):
        user = User.objects.create_user(
            auc_email="john@aucegypt.edu",
            auc_id="900260001",
            password="something-r@nd0m!",
        )

        assert user.auc_email == "john@aucegypt.edu"
        assert user.auc_id == "900260001"
        assert not user.is_staff
        assert not user.is_superuser
        assert user.check_password("something-r@nd0m!")
        assert user.username is None

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            auc_email="admin@aucegypt.edu",
            auc_id="900260002",
            password="something-r@nd0m!",
        )

        assert user.auc_email == "admin@aucegypt.edu"
        assert user.is_staff
        assert user.is_superuser
        assert user.username is None

    def test_create_superuser_username_ignored(self):
        user = User.objects.create_superuser(
            auc_email="test@aucegypt.edu",
            auc_id="900260003",
            password="something-r@nd0m!",
        )

        assert user.username is None

    def test_create_user_rejects_non_auc_email(self):
        with pytest.raises(ValueError, match="@aucegypt.edu"):
            User.objects.create_user(
                auc_email="john@gmail.edu",
                auc_id="900260004",
                password="something-r@nd0m!",
            )

    def test_create_user_rejects_empty_auc_id(self):
        with pytest.raises(ValueError, match="AUC ID"):
            User.objects.create_user(
                auc_email="john@aucegypt.edu",
                auc_id="",
                password="something-r@nd0m!",
            )

    def test_create_user_requires_auc_email(self):
        with pytest.raises(ValueError, match="AUC email must be set"):
            User.objects.create_user(
                auc_email="", auc_id="900260005", password="something-r@nd0m!"
            )


class TestAucIdValidation:
    def test_valid_auc_id_accepted(self):
        current_year_two_digit = date.today().year % 100
        auc_id = f"900{current_year_two_digit:02d}1234"
        user = User.objects.create_user(
            auc_email="valid@aucegypt.edu",
            auc_id=auc_id,
            password="something-r@nd0m!",
        )
        assert user.auc_id == auc_id

    def test_auc_id_rejects_wrong_prefix(self):
        with pytest.raises(ValueError, match="900"):
            User.objects.create_user(
                auc_email="wrongprefix@aucegypt.edu",
                auc_id="800261234",
                password="something-r@nd0m!",
            )

    def test_auc_id_rejects_wrong_length(self):
        with pytest.raises(ValueError, match="900"):
            User.objects.create_user(
                auc_email="shortid@aucegypt.edu",
                auc_id="9002612",
                password="something-r@nd0m!",
            )

    def test_auc_id_rejects_non_digit_characters(self):
        with pytest.raises(ValueError, match="900"):
            User.objects.create_user(
                auc_email="letters@aucegypt.edu",
                auc_id="900AB1234",
                password="something-r@nd0m!",
            )

    def test_auc_id_rejects_future_year(self):
        future_year_two_digit = (date.today().year + 1) % 100
        auc_id = f"900{future_year_two_digit:02d}1234"
        with pytest.raises(ValueError, match="future"):
            User.objects.create_user(
                auc_email="future@aucegypt.edu",
                auc_id=auc_id,
                password="something-r@nd0m!",
            )


def test_createsuperuser_command():
    out = StringIO()
    command_result = call_command(
        "createsuperuser",
        "--auc_email",
        "henry@aucegypt.edu",
        "--auc_id",
        "900260006",
        interactive=False,
        stdout=out,
    )
    assert command_result is None
    assert out.getvalue() == "Superuser created successfully.\n"
    user = User.objects.get(auc_email="henry@aucegypt.edu")
    assert not user.has_usable_password()
