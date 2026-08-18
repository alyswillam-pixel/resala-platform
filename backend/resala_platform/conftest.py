from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from resala_platform.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from resala_platform.users.models import User


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory.create()


@pytest.fixture
def admin_user(db, django_user_model):
    return django_user_model.objects.create_superuser(
        auc_email="admin@aucegypt.edu",
        auc_id="900000000",
        password="password",
    )
