from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from resala_platform.committees.models import CommitteeCapability
from resala_platform.committees.tests.factories import PASSWORD
from resala_platform.committees.tests.factories import CommitteeFactory
from resala_platform.committees.tests.factories import CommitteeRoleFactory
from resala_platform.committees.tests.factories import (
    PresidentialOfficeCommitteeFactory,
)
from resala_platform.committees.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def po_committee(db):
    return PresidentialOfficeCommitteeFactory()


@pytest.fixture
def po_director(po_committee):
    user = UserFactory(
        auc_email="po_director_cap@aucegypt.edu",
        auc_id="900000001",
        name="PO Director",
    )
    po_committee.director = user
    po_committee.save()
    user.refresh_from_db()
    return user


@pytest.fixture
def tech_committee(db):
    return CommitteeFactory(name="Tech Cap")


@pytest.fixture
def tech_director(tech_committee):
    user = UserFactory(
        auc_email="tech_director_cap@aucegypt.edu",
        auc_id="900000002",
        name="Tech Director",
    )
    tech_committee.director = user
    tech_committee.save()
    user.refresh_from_db()
    return user


@pytest.fixture
def tech_role(tech_committee):
    return CommitteeRoleFactory(committee=tech_committee, name="Builder Cap", order=1)


@pytest.fixture
def tech_member(tech_role):
    return UserFactory(
        auc_email="member_cap@aucegypt.edu",
        auc_id="900000003",
        name="Tech Member",
        committee_role=tech_role,
    )


def login(email):
    client = Client()
    assert client.login(username=email, password=PASSWORD)
    return client


class TestCommitteeCapabilityAdminScoping:
    def test_po_director_can_access_capability_changelist(self, po_director):
        client = login(po_director.auc_email)
        response = client.get(
            reverse("admin:committees_committeecapability_changelist"),
        )
        assert response.status_code == HTTPStatus.OK

    def test_po_director_can_add_capability(self, po_director, tech_committee):
        client = login(po_director.auc_email)
        response = client.post(
            reverse("admin:committees_committeecapability_add"),
            {
                "committee": str(tech_committee.pk),
                "capability": CommitteeCapability.Capability.EVENT_CREATION,
            },
        )

        assert CommitteeCapability.objects.filter(
            committee=tech_committee,
            capability=CommitteeCapability.Capability.EVENT_CREATION,
        ).exists()
        assert response.status_code in (HTTPStatus.FOUND, HTTPStatus.OK)

    def test_tech_director_cannot_access_capability_changelist(self, tech_director):
        client = login(tech_director.auc_email)
        response = client.get(
            reverse("admin:committees_committeecapability_changelist"),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_tech_director_cannot_add_capability(self, tech_director):
        client = login(tech_director.auc_email)
        response = client.get(reverse("admin:committees_committeecapability_add"))
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_regular_member_cannot_access_capability_changelist(self, tech_member):
        client = Client()
        assert client.login(username=tech_member.auc_email, password=PASSWORD)

        response = client.get(
            reverse("admin:committees_committeecapability_changelist"),
        )
        # Regular members are kicked to the login screen entirely
        assert response.status_code == HTTPStatus.FOUND
        assert "/admin/login/" in response.url
