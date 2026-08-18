import factory
from factory.django import DjangoModelFactory

from resala_platform.committees.models import Committee, CommitteeRole
from resala_platform.users.models import User


PASSWORD = "TestPassword123!"


class UserFactory(DjangoModelFactory):
    auc_email = factory.Sequence(lambda n: f"user{n}@aucegypt.edu")
    auc_id = factory.Sequence(lambda n: f"90000{n:04d}")
    name = "Test User"
    is_staff = False
    is_superuser = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", PASSWORD)

        user = model_class.objects.create_user(
            *args,
            password=password,
            **kwargs,
        )

        return user

    class Meta:
        model = User


class SuperUserFactory(UserFactory):
    auc_email = "root@aucegypt.edu"
    auc_id = "900000001"
    name = "Root Admin"
    is_staff = True
    is_superuser = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", PASSWORD)

        user = model_class.objects.create_superuser(
            *args,
            password=password,
            **kwargs,
        )

        return user


class CommitteeFactory(DjangoModelFactory[Committee]):
    name = factory.Sequence(lambda n: f"Committee {n}")
    description = factory.Faker("sentence")
    is_presidential_office = False
    director = None

    class Meta:
        model = Committee
        django_get_or_create = ["name"]


class PresidentialOfficeCommitteeFactory(CommitteeFactory):
    name = "Presidential Office"
    is_presidential_office = True


class CommitteeRoleFactory(DjangoModelFactory[CommitteeRole]):
    committee = factory.SubFactory(CommitteeFactory)
    name = factory.Sequence(lambda n: f"Role {n}")
    order = 1

    class Meta:
        model = CommitteeRole
