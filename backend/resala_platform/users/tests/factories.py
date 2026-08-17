from __future__ import annotations

import factory
from factory import post_generation
from factory.django import DjangoModelFactory

from resala_platform.users.models import User


class UserFactory(DjangoModelFactory[User]):
    auc_email = factory.Sequence(lambda n: f"user{n}@aucegypt.edu")
    auc_id = factory.Sequence(lambda n: f"90000{n}")
    name = factory.Faker("name")

    @post_generation
    def password(
        self: User,
        create: bool,  # noqa: FBT001
        extracted: str | None,
        **kwargs,
    ):
        password = (
            extracted
            if extracted
            else factory.Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )

        self.set_password(password)
        if create:
            self.save()

    class Meta:
        model = User
        django_get_or_create = ["auc_id"]
        skip_postgeneration_save = True
