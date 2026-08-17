import pytest

from resala_platform.users.models import User
from resala_platform.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestUser:
    def test_committee_role_is_optional(self):
        user = UserFactory()
        assert user.committee_role is None

    def test_auc_id_is_unique(self):
        UserFactory(auc_id="9000001")
        with pytest.raises(Exception):
            User.objects.create(
                auc_id="9000001", auc_email="some_different_email@aucegypt.edu"
            )

    def test_auc_email_unique(self):
        UserFactory(auc_email="dup@aucegypt.edu")
        with pytest.raises(Exception):
            User.objects.create(auc_id="different_id", auc_email="dup@aucegypt.edu")
