from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from resala_platform.committees.models import CommitteeRole
from resala_platform.committees.tests.factories import PASSWORD
from resala_platform.committees.tests.factories import CommitteeFactory
from resala_platform.committees.tests.factories import CommitteeRoleFactory
from resala_platform.committees.tests.factories import (
    PresidentialOfficeCommitteeFactory,
)
from resala_platform.committees.tests.factories import SuperUserFactory
from resala_platform.committees.tests.factories import UserFactory
from resala_platform.users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def superuser(db):
    return SuperUserFactory()


@pytest.fixture
def po_committee(db):
    return PresidentialOfficeCommitteeFactory()


@pytest.fixture
def po_director(po_committee):
    user = UserFactory(auc_email="nour@aucegypt.edu", auc_id="900000002", name="Nour")
    po_committee.director = user
    po_committee.save()
    user.refresh_from_db()
    return user


@pytest.fixture
def tech_committee(db):
    return CommitteeFactory(name="Tech")


@pytest.fixture
def ops_committee(db):
    return CommitteeFactory(name="Operations")


@pytest.fixture
def tech_director(tech_committee):
    user = UserFactory(auc_email="aly@aucegypt.edu", auc_id="900000003", name="Aly")
    tech_committee.director = user
    tech_committee.save()
    user.refresh_from_db()
    return user


@pytest.fixture
def ops_director(ops_committee):
    user = UserFactory(
        auc_email="mariam@aucegypt.edu",
        auc_id="900000004",
        name="Mariam",
    )
    ops_committee.director = user
    ops_committee.save()
    user.refresh_from_db()
    return user


@pytest.fixture
def tech_role(tech_committee):
    return CommitteeRoleFactory(committee=tech_committee, name="Builder", order=1)


@pytest.fixture
def ops_role(ops_committee):
    return CommitteeRoleFactory(committee=ops_committee, name="Coordinator", order=1)


@pytest.fixture
def tech_member(tech_role):
    return UserFactory(
        auc_email="member@aucegypt.edu",
        auc_id="900000005",
        name="Regular Member",
        committee_role=tech_role,
    )


def login(email):
    client = Client()
    assert client.login(username=email, password=PASSWORD)
    return client


class TestIsStaffSignal:
    def test_setting_director_grans_staff(self, tech_director):
        assert tech_director.is_staff is True

    def test_clearing_director_revokes_staff(self, tech_committee, tech_director):
        tech_committee.director = None
        tech_committee.save()
        tech_committee.refresh_from_db()
        tech_director.refresh_from_db()
        assert tech_director.is_staff is False

    def test_deleting_committee_revokes_staff(self, tech_committee, tech_director):
        tech_committee.delete()
        tech_director.refresh_from_db()
        assert tech_director.is_staff is False

    def test_regular_member_never_gets_staff(self, tech_member):
        assert tech_member.is_staff is False


class TestCommitteeAdminPresidentialOffice:
    def test_po_diector_can_access_committee_changelist(self, po_director):
        client = login(po_director.auc_email)
        response = client.get(reverse("admin:committees_committee_changelist"))
        assert response.status_code == HTTPStatus.OK

    def test_po_director_can_add_committee(self, po_director):
        client = login(po_director.auc_email)
        response = client.post(
            reverse("admin:committees_committee_add"),
            {
                "name": "Branding",
                "description": "",
                "is_presidential_office": False,
            },
        )

        assert CommitteeFactory._meta.model.objects.filter(name="Branding").exists()
        assert response.status_code in (HTTPStatus.FOUND, HTTPStatus.OK)

    def test_tech_director_cannot_access_committee_changelist(self, tech_director):
        client = login(tech_director.auc_email)
        response = client.get(reverse("admin:committees_committee_changelist"))
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_tech_director_cannot_access_committee_add_page(self, tech_director):
        client = login(tech_director.auc_email)
        response = client.get(reverse("admin:committees_committee_add"))
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_regular_member_cannot_reach_admin_at_all(self, tech_member):
        client = Client()
        assert client.login(username=tech_member.auc_email, password=PASSWORD)

        response = client.get(reverse("admin:index"))
        assert response.status_code == HTTPStatus.FOUND
        assert "/admin/login/" in response.url


class TestCommitteeRoleAdminScoping:
    def test_tech_director_changelist_excludes_other_committees_roles(
        self,
        tech_director,
        tech_role,
        ops_role,
    ):
        client = login(tech_director.auc_email)
        response = client.get(reverse("admin:committees_committeerole_changelist"))
        assert response.status_code == HTTPStatus.OK

        object_list = response.context["cl"].queryset
        assert tech_role in object_list
        assert ops_role not in object_list

    def test_tech_director_can_view_own_role(self, tech_director, tech_role):
        client = login(tech_director.auc_email)
        response = client.get(
            reverse("admin:committees_committeerole_change", args=[tech_role.pk]),
        )
        assert response.status_code == HTTPStatus.OK

    def test_tech_director_cannot_view_other_committees_role(
        self,
        tech_director,
        ops_role,
    ):
        client = login(tech_director.auc_email)
        response = client.get(
            reverse("admin:committees_committeerole_change", args=[ops_role.pk]),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_tech_director_can_create_role_in_own_committee(
        self,
        tech_director,
        tech_committee,
    ):
        client = login(tech_director.auc_email)
        response = client.post(
            reverse("admin:committees_committeerole_add"),
            {"committee": str(tech_committee.pk), "name": "Verifier", "order": 2},
        )
        assert CommitteeRole.objects.filter(
            committee=tech_committee,
            name="Verifier",
        ).exists()
        assert response.status_code in (HTTPStatus.FOUND, HTTPStatus.OK)

    def test_tech_director_cannot_create_role_in_other_committee(
        self,
        tech_director,
        ops_committee,
    ):
        client = login(tech_director.auc_email)
        response = client.post(
            reverse("admin:committees_committeerole_add"),
            {
                "committee": str(ops_committee.pk),
                "name": "Smuggled role",
                # didn't find a good name there so, that comes from smuggle
                # shipment :) Bad pun?
                "order": 1,
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert not CommitteeRole.objects.filter(name="Smuggled role").exists()

    def test_tech_director_add_form_only_offers_own_committee(
        self,
        tech_director,
        tech_committee,
        ops_committee,
    ):
        client = login(tech_director.auc_email)
        response = client.get(reverse("admin:committees_committeerole_add"))
        form = response.context["adminform"].form
        choices = list(form.fields["committee"].queryset)
        assert choices == [tech_committee]


class TestUserAdminScoping:
    def test_tech_director_user_changelist_excludes_other_committees_members(
        self,
        tech_director,
        tech_member,
        tech_role,
        ops_role,
    ):
        other_member = UserFactory(
            auc_email="other@aucegypt.edu",
            auc_id="900000006",
            name="Other Member",
            committee_role=ops_role,
        )

        client = login(tech_director.auc_email)
        response = client.get(reverse("admin:users_user_changelist"))
        object_list = response.context["cl"].queryset
        assert tech_member in object_list
        assert other_member not in object_list

    def test_tech_director_cannot_view_user_from_other_committee(
        self,
        tech_director,
        ops_role,
    ):
        other_member = UserFactory(
            auc_email="other2@aucegypt.edu",
            auc_id="900000007",
            name="Other Member Two",
            committee_role=ops_role,
        )

        client = login(tech_director.auc_email)
        response = client.get(
            reverse("admin:users_user_change", args=[other_member.pk]),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_tech_director_user_form_role_field_restricted_to_own_committee(
        self,
        tech_director,
        tech_role,
        ops_role,
    ):
        client = login(tech_director.auc_email)
        response = client.get(reverse("admin:users_user_add"))
        form = response.context["adminform"].form
        choices = list(form.fields["committee_role"].queryset)
        assert choices == [tech_role]

    def test_tech_director_cannot_assign_user_to_other_committee_role(
        self,
        tech_director,
        ops_role,
    ):
        client = login(tech_director.auc_email)
        response = client.post(
            reverse("admin:users_user_add"),
            {
                "auc_email": "smuggled@aucegypt.edu",
                "auc_id": "900000008",
                "committee_role": str(ops_role.pk),
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert not User.objects.filter(auc_email="smiggled@aucegypt.edu").exists()

    def test_tech_director_cannot_grant_staff_via_fieldsets(
        self,
        tech_director,
        tech_member,
    ):
        client = login(tech_director.auc_email)
        response = client.get(
            reverse("admin:users_user_change", args=[tech_member.pk]),
        )
        form = response.context["adminform"].form
        assert "is_staff" not in form.fields
        assert "is_superuser" not in form.fields
