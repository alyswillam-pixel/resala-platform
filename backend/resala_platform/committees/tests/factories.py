import factory
from factory.django import DjangoModelFactory

from resala_platform.committees.models import Committee
from resala_platform.committees.models import CommitteeRole


class CommitteeFactory(DjangoModelFactory[Committee]):
    name = factory.Sequence(lambda n: f"Committe {n}")
    description = factory.Faker("sentence")

    class Meta:
        model = Committee
        django_get_or_create = ["name"]


class CommitteeRoleFactory(DjangoModelFactory[CommitteeRole]):
    committee = factory.SubFactory(CommitteeFactory)
    name = factory.Sequence(lambda n: f"Role {n}")

    class Meta:
        model = CommitteeRole
