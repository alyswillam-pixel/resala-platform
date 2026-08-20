from http import HTTPStatus

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from resala_platform.committees.models import CommitteeCapability
from resala_platform.committees.tests.factories import CommitteeFactory
from resala_platform.committees.tests.factories import CommitteeRoleFactory
from resala_platform.committees.tests.factories import (
    PresidentialOfficeCommitteeFactory,
)
from resala_platform.events.models import EventStateTransition
from resala_platform.events.tests.factories import BudgetFactory
from resala_platform.events.tests.factories import EventFactory
from resala_platform.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def requester():
    return UserFactory()


@pytest.fixture
def treasurer():
    committee = CommitteeFactory(name="Treasury")
    CommitteeCapability.objects.create(
        committee=committee,
        capability=CommitteeCapability.Capability.TREASURY,
    )
    role = CommitteeRoleFactory(name="Treasurer", committee=committee)
    return UserFactory(committee_role=role)


@pytest.fixture
def po_leader():
    po = PresidentialOfficeCommitteeFactory()
    leader = UserFactory()
    po.director = leader
    po.save()
    leader.refresh_from_db()
    return leader


@pytest.fixture
def event_creator():
    committee = CommitteeFactory(name="Events Team")
    CommitteeCapability.objects.create(
        committee=committee,
        capability=CommitteeCapability.Capability.EVENT_CREATION,
    )
    role = CommitteeRoleFactory(name="Event Coordinator", committee=committee)
    return UserFactory(committee_role=role)


@pytest.fixture
def event(requester):
    evt = EventFactory(requester=requester)
    BudgetFactory(event=evt)
    return evt


def transition_url(name, event):
    return reverse(
        f"api:event-{name.replace('_', '-')}",
        kwargs={"pk": event.pk},
    )


class TestEventWorkflowAPI:
    def test_full_chain_and_audit_trail(self, api_client, event, requester, treasurer):
        api_client.force_authenticate(user=requester)
        response = api_client.post(transition_url("submit_for_budget_review", event))
        assert response.status_code == HTTPStatus.OK

        event.refresh_from_db()
        assert event.current_state == "Pending Treasurer Review"
        assert event.budget.status == "Pending Treasurer Review"

        transition = EventStateTransition.objects.first()
        assert transition.event == event
        assert transition.action == "submit_for_budget_review"
        assert transition.actor == requester
        assert transition.from_state == "Draft"
        assert transition.to_state == "Pending Treasurer Review"

        api_client.force_authenticate(user=treasurer)
        response = api_client.post(transition_url("treasurer_approve_budget", event))
        assert response.status_code == HTTPStatus.OK

        event.refresh_from_db()
        assert event.current_state == "Budget Approved"
        assert event.budget.status == "Approved"
        assert event.budget.approved_by == treasurer

        transition = EventStateTransition.objects.first()
        assert transition.action == "treasurer_approve_budget"
        assert transition.actor == treasurer

    def test_unauthorized_transition_returns_403_and_leaves_state_unchanged(
        self,
        api_client,
        event,
        treasurer,
    ):
        api_client.force_authenticate(user=treasurer)
        response = api_client.post(transition_url("submit_for_budget_review", event))
        assert response.status_code == HTTPStatus.FORBIDDEN

        event.refresh_from_db()
        assert event.current_state == "Draft"
        assert not EventStateTransition.objects.exists()

    def test_invalid_sequence_returns_400(self, api_client, event, requester):
        api_client.force_authenticate(user=requester)
        response = api_client.post(transition_url("activate_event", event))
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_unregistered_committee_member_gets_403_on_approve(
        self,
        api_client,
        event,
        requester,
    ):
        committee = CommitteeFactory(name="Branding")
        role = CommitteeRoleFactory(name="Head of Branding", committee=committee)
        outsider = UserFactory(committee_role=role)

        api_client.force_authenticate(user=requester)
        api_client.post(transition_url("submit_for_budget_review", event))

        api_client.force_authenticate(user=outsider)
        response = api_client.post(transition_url("treasurer_approve_budget", event))
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_president_can_approve_after_escalation(
        self,
        api_client,
        event,
        requester,
        treasurer,
        po_leader,
    ):
        api_client.force_authenticate(user=requester)
        api_client.post(transition_url("submit_for_budget_review", event))
        api_client.force_authenticate(user=treasurer)
        response = api_client.post(transition_url("treasurer_escalate_budget", event))
        assert response.status_code == HTTPStatus.OK

        api_client.force_authenticate(user=po_leader)
        response = api_client.post(transition_url("president_approve_budget", event))
        assert response.status_code == HTTPStatus.OK

        event.refresh_from_db()
        assert event.current_state == "Budget Approved"
        assert event.budget.approved_by == po_leader

    def test_unauthenticated_request_is_rejected(self, api_client, event):
        response = api_client.post(transition_url("submit_for_budget_review", event))
        assert response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)


class TestBudgetViewSetPermissions:
    def test_requester_can_create_budget_for_own_draft_event(
        self,
        api_client,
        requester,
    ):
        api_client.force_authenticate(user=requester)
        event = EventFactory(requester=requester)
        response = api_client.post(
            reverse("api:budget-list"),
            {
                "event": str(event.pk),
                "amount": "150.0",
            },
        )
        assert response.status_code == HTTPStatus.CREATED

    def test_cannot_create_budget_for_someone_elses_event(self, api_client, requester):
        other = UserFactory()
        event = EventFactory(requester=other)
        api_client.force_authenticate(user=requester)
        response = api_client.post(
            reverse("api:budget-list"),
            {
                "event": str(event.pk),
                "amount": "150.0",
            },
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_cannot_create_second_budget_for_same_event(
        self,
        api_client,
        event,
        requester,
    ):
        api_client.force_authenticate(user=requester)
        response = api_client.post(
            reverse("api:budget-list"),
            {
                "event": str(event.pk),
                "amount": "999.00",
            },
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_cannot_update_budget_once_event_leaves_draft(
        self,
        api_client,
        event,
        requester,
        treasurer,
    ):
        api_client.force_authenticate(user=requester)
        api_client.post(transition_url("submit_for_budget_review", event))
        response = api_client.patch(
            reverse("api:budget-detail", kwargs={"pk": event.budget.pk}),
            {
                "amount": "1.00",
            },
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_owner_can_update_budget_while_draft(self, api_client, event, requester):
        api_client.force_authenticate(user=requester)
        response = api_client.patch(
            reverse("api:budget-detail", kwargs={"pk": event.budget.pk}),
            {
                "amount": "42.00",
            },
        )
        assert response.status_code == HTTPStatus.OK


class TestEventCreationPermissions:
    def test_authorized_committee_member_can_create_event(
        self,
        api_client,
        event_creator,
    ):
        api_client.force_authenticate(user=event_creator)
        response = api_client.post(
            reverse("api:event-list"),
            {
                "title": "Annual Tech Symposium",
                "description": {"topic": "AI and Future"},
                "requester": str(event_creator.pk),
            },
            format="json",
        )
        assert response.status_code == HTTPStatus.CREATED

    def test_unauthorized_committee_member_cannot_create_event(
        self,
        api_client,
        requester,
    ):
        api_client.force_authenticate(user=requester)
        response = api_client.post(
            reverse("api:event-list"),
            {"title": "Unauthorized Hackathon", "requester": str(requester.pk)},
            format="json",
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert (
            response.json()["detail"]
            == "Your committee is not authorized to create events."
        )

    def test_unauthenticated_user_cannot_create_event(self, api_client):
        response = api_client.post(
            reverse("api:event-list"),
            {"title": "Ghost Event"},
            format="json",
        )
        assert response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)
