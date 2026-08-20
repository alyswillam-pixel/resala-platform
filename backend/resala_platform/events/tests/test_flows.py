import pytest

from resala_platform.committees.tests.factories import CommitteeFactory
from resala_platform.committees.tests.factories import CommitteeRoleFactory
from resala_platform.committees.tests.factories import (
    PresidentialOfficeCommitteeFactory,
)
from resala_platform.events.flows import EventFlow
from resala_platform.events.models import EventState
from resala_platform.events.models import TreasuryCommittee
from resala_platform.events.tests.factories import BudgetFactory
from resala_platform.events.tests.factories import EventFactory
from resala_platform.events.tests.factories import TreasuryCommitteeFactory
from resala_platform.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def requester():
    return UserFactory()


@pytest.fixture
def treasurer():
    committee = CommitteeFactory(name="Treasury")
    TreasuryCommitteeFactory(committee=committee)
    role = CommitteeRoleFactory(name="Treasurer", committee=committee)
    return UserFactory(committee_role=role)


@pytest.fixture
def unregistered_committee_member():
    committee = CommitteeFactory(name="Branding")
    role = CommitteeRoleFactory(name="Head of Branding", committee=committee)
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
def event(requester):
    evt = EventFactory(requester=requester)
    BudgetFactory(event=evt)
    return evt


class TestHappyPathViaTreasurer:
    def test_full_chain_draft_to_completed(self, event, requester, treasurer):
        flow = EventFlow(event)
        assert flow.submit_for_budget_review.can_proceed()

        flow.submit_for_budget_review(by_user=requester)
        event.save()
        assert event.current_state == EventState.PENDING_TREASURER_REVIEW

        flow = EventFlow(event)
        flow.treasurer_approve_budget(by_user=treasurer)
        event.save()
        assert event.current_state == EventState.BUDGET_APPROVED
        assert event.budget.status == "Approved"
        assert event.budget.approved_by == treasurer

        flow = EventFlow(event)
        flow.activate_event(by_user=requester)
        event.save()
        assert event.current_state == EventState.ACTIVE

        flow = EventFlow(event)
        flow.complete_event(by_user=requester)
        event.save()
        assert event.current_state == EventState.COMPLETED


class TestEscalationPath:
    def test_treasurer_escalate_then_po_approved(self, event, treasurer, po_leader):
        flow = EventFlow(event)
        flow.submit_for_budget_review(by_user=event.requester)
        event.save()

        flow = EventFlow(event)
        assert flow.treasurer_escalate_budget.can_proceed()
        flow.treasurer_escalate_budget(by_user=treasurer)
        event.save()
        assert event.current_state == EventState.PENDING_PRESIDENTIAL_REVIEW
        assert event.budget.status == EventState.PENDING_PRESIDENTIAL_REVIEW

        flow = EventFlow(event)
        assert not flow.president_approve_budget.has_perm(treasurer)
        assert flow.president_approve_budget.has_perm(po_leader)
        flow.president_approve_budget(by_user=po_leader)
        event.save()
        assert event.current_state == EventState.BUDGET_APPROVED
        assert event.budget.approved_by == po_leader


class TestRejectionPath:
    def test_reject_then_revise_returns_to_draft(self, event, treasurer):
        flow = EventFlow(event)
        flow.submit_for_budget_review(by_user=event.requester)
        event.save()

        flow = EventFlow(event)
        flow.reject_budget(by_user=treasurer)
        event.save()
        assert event.current_state == EventState.BUDGET_REJECTED
        assert event.budget.status == "Rejected"

        flow = EventFlow(event)
        flow.revise_budget(by_user=event.requester)
        event.save()
        assert event.current_state == EventState.DRAFT
        assert event.budget.status == "Pending"
        assert event.budget.approved_by is None

    def test_reject_then_turn_down_is_terminal(self, event, treasurer):
        flow = EventFlow(event)
        flow.submit_for_budget_review(by_user=event.requester)
        event.save()
        flow = EventFlow(event)
        flow.reject_budget(by_user=treasurer)
        event.save()

        flow = EventFlow(event)
        flow.turn_down_event(by_user=treasurer)
        event.save()
        assert event.current_state == EventState.TURNED_DOWN

        flow = EventFlow(event)
        assert not flow.revise_budget.can_proceed()
        assert not flow.submit_for_budget_review.can_proceed()


class TestPermissionEnforcement:
    def test_only_requester_can_submit(self, event, treasurer):
        flow = EventFlow(event)
        assert not flow.submit_for_budget_review.has_perm(treasurer)
        assert flow.submit_for_budget_review.has_perm(event.requester)

    def test_unregistered_committee_member_cannot_approve(
        self,
        event,
        unregistered_committee_member,
    ):
        flow = EventFlow(event)
        flow.submit_for_budget_review(by_user=event.requester)
        event.save()

        flow = EventFlow(event)
        assert not flow.treasurer_approve_budget.has_perm(unregistered_committee_member)

    def test_registering_committee_grants_approval_immediately(
        self,
        event,
        unregistered_committee_member,
    ):
        flow = EventFlow(event)
        flow.submit_for_budget_review(by_user=event.requester)
        event.save()

        flow = EventFlow(event)
        assert not flow.treasurer_approve_budget.has_perm(unregistered_committee_member)

        TreasuryCommitteeFactory(
            committee=unregistered_committee_member.committee_role.committee,
        )

        flow = EventFlow(event)
        assert flow.treasurer_approve_budget.has_perm(unregistered_committee_member)

    def test_removing_committee_revokes_approval(self, event, treasurer):
        flow = EventFlow(event)
        flow.submit_for_budget_review(by_user=event.requester)
        event.save()

        flow = EventFlow(event)
        assert flow.treasurer_approve_budget.has_perm(treasurer)

        TreasuryCommittee.objects.filter(
            committee=treasurer.committee_role.committee,
        ).delete()

        flow = EventFlow(event)
        assert not flow.treasurer_approve_budget.has_perm(treasurer)


class TestInvalidSequences:
    def test_cannot_activate_before_approval(self, event):
        flow = EventFlow(event)
        assert not flow.activate_event.can_proceed()

    def test_cannot_approve_from_draft(self, event, treasurer):
        flow = EventFlow(event)
        assert not flow.treasurer_approve_budget.can_proceed()
