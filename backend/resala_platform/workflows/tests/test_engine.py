import pytest
from django.contrib.contenttypes.models import ContentType

from resala_platform.committees.models import CommitteeCapability
from resala_platform.workflows.engine import InvalidTransitionError
from resala_platform.workflows.engine import UnAuthorizedTransitionError
from resala_platform.workflows.engine import WorkflowEngine
from resala_platform.workflows.engine import WorkflowError
from resala_platform.workflows.engine import WorkflowService
from resala_platform.workflows.models import AuthorizationType
from resala_platform.workflows.models import WorkflowActionType
from resala_platform.workflows.models import WorkflowInstance
from resala_platform.workflows.models import WorkflowTransitionAction
from resala_platform.workflows.tests.factories import BudgetFactory
from resala_platform.workflows.tests.factories import CommitteeCapabilityFactory
from resala_platform.workflows.tests.factories import CommitteeRoleFactory
from resala_platform.workflows.tests.factories import EventFactory
from resala_platform.workflows.tests.factories import UserFactory
from resala_platform.workflows.tests.factories import WorkflowFactory
from resala_platform.workflows.tests.factories import WorkflowStateFactory
from resala_platform.workflows.tests.factories import WorkflowTransitionFactory

pytestmark = pytest.mark.django_db


class TestWorkflowService:
    def test_start_creates_instance_at_initial_state(self):
        workflow = WorkflowFactory()
        initial_state = WorkflowStateFactory(workflow=workflow, is_initial=True)
        event = EventFactory()
        instance = WorkflowService.start(obj=event, workflow=workflow)

        assert instance.workflow == workflow
        assert instance.current_state == initial_state
        assert instance.content_object == event

    def test_cannot_start_same_object_twice(self):
        workflow = WorkflowFactory()
        WorkflowStateFactory(workflow=workflow, is_initial=True)
        event = EventFactory()
        WorkflowService.start(obj=event, workflow=workflow)

        with pytest.raises(WorkflowError):
            WorkflowService.start(obj=event, workflow=workflow)


class TestWorkflowEngine:
    def setup_method(self):
        self.workflow = WorkflowFactory()
        self.source = WorkflowStateFactory(workflow=self.workflow)
        self.target = WorkflowStateFactory(workflow=self.workflow)
        self.transition = WorkflowTransitionFactory(
            workflow=self.workflow,
            source=self.source,
            target=self.target,
        )
        self.requester = UserFactory()
        self.event = EventFactory(requester=self.requester)
        self.instance = WorkflowInstance.objects.create(
            workflow=self.workflow,
            current_state=self.source,
            content_type=ContentType.objects.get_for_model(self.event),
            object_id=self.event.pk,
        )

    def test_transition_is_available_from_current_state(self):
        self.transition.rules.create(authorization_type=AuthorizationType.REQUESTER)
        engine = WorkflowEngine(self.instance)

        assert engine.can_execute(self.transition, self.requester)

    def test_transition_not_available_from_wrong_state(self):
        current = WorkflowStateFactory(workflow=self.workflow)
        self.instance.current_state = current
        self.instance.save()

        self.transition.rules.create(authorization_type=AuthorizationType.REQUESTER)
        engine = WorkflowEngine(self.instance)

        assert not engine.can_execute(self.transition, self.requester)

    def test_requester_rule_allows_event_requester(self):
        self.transition.rules.create(authorization_type=AuthorizationType.REQUESTER)

        assert WorkflowEngine(self.instance).can_execute(
            self.transition,
            self.requester,
        )

    def test_requester_rule_rejects_other_user(self):
        other_user = UserFactory()
        self.transition.rules.create(authorization_type=AuthorizationType.REQUESTER)

        assert not WorkflowEngine(self.instance).can_execute(
            self.transition,
            other_user,
        )

    def test_capability_rule_allows_user_from_capable_committee(self):
        committee_role = CommitteeRoleFactory()
        user = UserFactory(committee_role=committee_role)
        CommitteeCapabilityFactory(
            committee=committee_role.committee,
            capability=CommitteeCapability.Capability.TREASURY,
        )
        self.transition.rules.create(
            authorization_type=AuthorizationType.CAPABILITY,
            capability=CommitteeCapability.Capability.TREASURY,
        )

        assert WorkflowEngine(self.instance).can_execute(self.transition, user)

    def test_capability_rule_rejects_user_without_capability(self):
        committee_role = CommitteeRoleFactory()
        user = UserFactory(committee_role=committee_role)
        self.transition.rules.create(
            authorization_type=AuthorizationType.CAPABILITY,
            capability=CommitteeCapability.Capability.TREASURY,
        )

        assert not WorkflowEngine(self.instance).can_execute(self.transition, user)

    def test_multiple_rules_are_or_logic(self):
        self.transition.rules.create(authorization_type=AuthorizationType.REQUESTER)
        self.transition.rules.create(
            authorization_type=AuthorizationType.CAPABILITY,
            capability=CommitteeCapability.Capability.TREASURY,
        )

        assert WorkflowEngine(self.instance).can_execute(
            self.transition,
            self.requester,
        )

    def test_execute_changes_state(self):
        self.transition.rules.create(authorization_type=AuthorizationType.REQUESTER)
        result = WorkflowEngine(self.instance).execute(
            transition=self.transition,
            user=self.requester,
        )
        result.refresh_from_db()

        assert result.current_state == self.target

    def test_execute_creates_transition_log(self):
        self.transition.rules.create(authorization_type=AuthorizationType.REQUESTER)
        WorkflowEngine(self.instance).execute(
            transition=self.transition,
            user=self.requester,
            note="Test transition",
        )
        log = self.instance.transition_logs.get()

        assert log.transition == self.transition
        assert log.from_state == self.source
        assert log.to_state == self.target
        assert log.actor == self.requester
        assert log.note == "Test transition"

    def test_execute_rejects_unauthorized_user(self):
        other_user = UserFactory()
        self.transition.rules.create(authorization_type=AuthorizationType.REQUESTER)

        with pytest.raises(UnAuthorizedTransitionError):
            WorkflowEngine(self.instance).execute(
                transition=self.transition,
                user=other_user,
            )

    def test_execute_rejects_wrong_source_state(self):
        current = WorkflowStateFactory(workflow=self.workflow)
        self.instance.current_state = current
        self.instance.save()

        self.transition.rules.create(authorization_type=AuthorizationType.REQUESTER)

        with pytest.raises(InvalidTransitionError):
            WorkflowEngine(self.instance).execute(
                transition=self.transition,
                user=self.requester,
            )

    def test_set_budget_status_action(self):
        BudgetFactory(event=self.event, status="Pending")
        self.transition.rules.create(authorization_type=AuthorizationType.REQUESTER)
        WorkflowTransitionAction.objects.create(
            transition=self.transition,
            action_type=WorkflowActionType.SET_BUDGET_STATUS,
            value="Approved",
        )
        WorkflowEngine(self.instance).execute(
            transition=self.transition,
            user=self.requester,
        )
        self.event.budget.refresh_from_db()

        assert self.event.budget.status == "Approved"

    def test_set_budget_approver_action(self):
        BudgetFactory(event=self.event)
        self.transition.rules.create(authorization_type=AuthorizationType.REQUESTER)
        WorkflowTransitionAction.objects.create(
            transition=self.transition,
            action_type=WorkflowActionType.SET_BUDGET_APPROVER,
        )
        WorkflowEngine(self.instance).execute(
            transition=self.transition,
            user=self.requester,
        )
        self.event.budget.refresh_from_db()

        assert self.event.budget.approved_by == self.requester

    def test_clear_budget_approver_action(self):
        approver = UserFactory()
        BudgetFactory(event=self.event, approved_by=approver)
        self.transition.rules.create(authorization_type=AuthorizationType.REQUESTER)
        WorkflowTransitionAction.objects.create(
            transition=self.transition,
            action_type=WorkflowActionType.CLEAR_BUDGET_APPROVER,
        )
        WorkflowEngine(self.instance).execute(
            transition=self.transition,
            user=self.requester,
        )
        self.event.budget.refresh_from_db()

        assert self.event.budget.approved_by is None
