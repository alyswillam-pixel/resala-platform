from __future__ import annotations

import factory
from factory.django import DjangoModelFactory

from resala_platform.committees.tests.factories import CommitteeFactory
from resala_platform.events.models import Budget
from resala_platform.events.models import Event
from resala_platform.events.models import TreasuryCommittee
from resala_platform.users.tests.factories import UserFactory


class EventFactory(DjangoModelFactory):
    title = factory.Faker("sentence", nb_words=4)
    description = factory.LazyFunction(dict)
    requester = factory.SubFactory(UserFactory)

    class Meta:
        model = Event


class BudgetFactory(DjangoModelFactory):
    event = factory.SubFactory(EventFactory)
    amount = factory.Faker(
        "pydecimal",
        left_digits=4,
        right_digits=2,
        positive=True,
    )

    class Meta:
        model = Budget


class TreasuryCommitteeFactory(DjangoModelFactory):
    committee = factory.SubFactory(CommitteeFactory)

    class Meta:
        model = TreasuryCommittee
        django_get_or_create = ["committee"]
