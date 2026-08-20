import pytest

from resala_platform.committees.models import CommitteeCapability
from resala_platform.committees.permissions import committee_has_capability
from resala_platform.committees.tests.factories import CommitteeCapabilityFactory
from resala_platform.committees.tests.factories import CommitteeFactory

pytestmark = pytest.mark.django_db


class TestCommitteeHasCapability:
    def test_returns_true_when_capability_exists(self):
        committee = CommitteeFactory()
        CommitteeCapabilityFactory(
            committee=committee,
            capability=CommitteeCapability.Capability.TREASURY,
        )
        assert (
            committee_has_capability(
                committee.id,
                CommitteeCapability.Capability.TREASURY,
            )
            is True
        )

    def test_returns_false_when_capability_missing(self):
        committee = CommitteeFactory()
        CommitteeCapabilityFactory(
            committee=committee,
            capability=CommitteeCapability.Capability.EVENT_CREATION,
        )
        assert (
            committee_has_capability(
                committee.id,
                CommitteeCapability.Capability.TREASURY,
            )
            is False
        )

    def test_false_when_committee_id_is_none(self):
        assert (
            committee_has_capability(None, CommitteeCapability.Capability.TREASURY)
            is False
        )
