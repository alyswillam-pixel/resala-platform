from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from resala_platform.committees.tests.factories import CommitteeFactory
from resala_platform.committees.tests.factories import (
    PresidentialOfficeCommitteeFactory,
)
from resala_platform.events.models import TreasuryCommittee
from resala_platform.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


PASSWORD = "TestPassword123!"


def login_as(user):
    client = Client()
    assert client.login(username=user.auc_email, password=PASSWORD)
    return client


@pytest.fixture
def po_director():
    po = PresidentialOfficeCommitteeFactory()
    leader = UserFactory(password=PASSWORD)
    po.director = leader
    po.save()
    leader.refresh_from_db()
    return leader


@pytest.fixture
def committee_director():
    committee = CommitteeFactory(name="Tech")
    director = UserFactory(password=PASSWORD)
    committee.director = director
    committee.save()
    director.refresh_from_db()
    return director


class TestTreasuryCommitteeAdminScoping:
    def test_po_director_can_access(self, po_director):
        client = login_as(po_director)
        response = client.get(reverse("admin:events_treasurycommittee_changelist"))
        assert response.status_code == HTTPStatus.OK

    def test_po_director_can_register_a_committee(self, po_director):
        committee = CommitteeFactory(name="Finance")
        client = login_as(po_director)
        response = client.post(
            reverse("admin:events_treasurycommittee_add"),
            {
                "committee": str(committee.pk),
            },
        )
        assert TreasuryCommittee.objects.filter(committee=committee).exists()
        assert response.status_code in (HTTPStatus.FOUND, HTTPStatus.OK)

    def test_ordinary_committee_director_cannot_access(self, committee_director):
        client = login_as(committee_director)
        response = client.get(reverse("admin:events_treasurycommittee_changelist"))
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_ordinary_committee_director_cannot_register_own_committee(
        self,
        committee_director,
    ):
        client = login_as(committee_director)
        response = client.post(
            reverse("admin:events_treasurycommittee_add"),
            {
                "committee": str(committee_director.directed_committees.first().pk),
            },
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert not TreasuryCommittee.objects.exists()
