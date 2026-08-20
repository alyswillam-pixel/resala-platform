import pytest
from django.db import IntegrityError

from resala_platform.committees.models import Committee
from resala_platform.committees.models import CommitteeCapability
from resala_platform.committees.models import CommitteeRole
from resala_platform.committees.tests.factories import CommitteeCapabilityFactory
from resala_platform.committees.tests.factories import CommitteeFactory
from resala_platform.committees.tests.factories import CommitteeRoleFactory

pytestmark = pytest.mark.django_db


class TestCommittee:
    def test_str(self):
        committee = CommitteeFactory(name="Tech")
        assert str(committee) == "Tech"

    def test_name_is_unique(self):
        CommitteeFactory(name="Tech")
        with pytest.raises(IntegrityError):
            Committee.objects.create(name="Tech")

    def test_director_is_optional(self):
        commitee = CommitteeFactory()
        assert commitee.director is None
        assert commitee.vice_director is None


class TestCommitteeRole:
    def test_str(self):
        committee = CommitteeFactory(name="Tech")
        role = CommitteeRoleFactory(committee=committee, name="Navigator")
        assert str(role) == "Tech — Navigator"

    def test_role_name_unique_within_commitee(self):
        committee = CommitteeFactory()
        CommitteeRoleFactory(committee=committee, name="Navigator")
        with pytest.raises(IntegrityError):
            CommitteeRole.objects.create(committee=committee, name="Navigator")

    def test_same_role_name_allowed_across_committee(self):
        committee_a = CommitteeFactory()
        committee_b = CommitteeFactory()
        CommitteeRoleFactory(committee=committee_a, name="Navigator")
        CommitteeRoleFactory(committee=committee_b, name="Navigator")


class TestCommitteeCapability:
    def test_str(self):
        committee = CommitteeFactory(name="Tech")
        capability = CommitteeCapabilityFactory(
            committee=committee,
            capability=CommitteeCapability.Capability.TREASURY,
        )
        assert str(capability) == "Tech — Treasury / Budget Approval"

    def test_unique_together_constraint(self):
        committee = CommitteeFactory()
        CommitteeCapabilityFactory(
            committee=committee,
            capability=CommitteeCapability.Capability.EVENT_CREATION,
        )

        with pytest.raises(IntegrityError):
            CommitteeCapability.objects.create(
                committee=committee,
                capability=CommitteeCapability.Capability.EVENT_CREATION,
            )
