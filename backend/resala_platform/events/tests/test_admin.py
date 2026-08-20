import pytest
from django.test import Client

from resala_platform.committees.tests.factories import CommitteeFactory
from resala_platform.committees.tests.factories import (
    PresidentialOfficeCommitteeFactory,
)
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
