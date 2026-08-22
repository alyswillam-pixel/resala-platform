import pytest
from django.core.exceptions import ValidationError

from resala_platform.workflows.models import AuthorizationType
from resala_platform.workflows.models import WorkflowTransitionRule
from resala_platform.workflows.tests.factories import WorkflowFactory
from resala_platform.workflows.tests.factories import WorkflowStateFactory
from resala_platform.workflows.tests.factories import WorkflowTransitionFactory

pytestmark = pytest.mark.django_db


class TestWorkflowState:
    def test_state_must_belong_to_workflow(self):
        workflow_a = WorkflowFactory()
        workflow_b = WorkflowFactory()

        state = WorkflowStateFactory(workflow=workflow_a)
        transition = WorkflowTransitionFactory(workflow=workflow_b, source=state)

        with pytest.raises(ValidationError):
            transition.full_clean()


class TestWorkflowTransition:
    def test_source_and_target_must_belong_to_workflow(self):
        workflow = WorkflowFactory()
        another_workflow = WorkflowFactory()
        source = WorkflowStateFactory(workflow=workflow)
        target = WorkflowStateFactory(workflow=another_workflow)
        transition = WorkflowTransitionFactory(
            workflow=workflow,
            source=source,
            target=target,
        )

        with pytest.raises(ValidationError):
            transition.full_clean()


class TestWorkflowTransitionRule:
    def test_capability_rule_requires_capability(self):
        transition = WorkflowTransitionFactory()
        rule = WorkflowTransitionRule(
            transition=transition,
            authorization_type=AuthorizationType.CAPABILITY,
        )

        with pytest.raises(ValidationError):
            rule.full_clean()

    def test_committee_member_rule_requires_committee(self):
        transition = WorkflowTransitionFactory()
        rule = WorkflowTransitionRule(
            transition=transition,
            authorization_type=AuthorizationType.COMMITTEE_MEMBER,
        )

        with pytest.raises(ValidationError):
            rule.full_clean()

    def test_committee_leader_rule_requires_committee(self):
        transition = WorkflowTransitionFactory()
        rule = WorkflowTransitionRule(
            transition=transition,
            authorization_type=AuthorizationType.COMMITTEE_LEADER,
        )

        with pytest.raises(ValidationError):
            rule.full_clean()

    def test_capability_rule_can_be_created(self):
        transition = WorkflowTransitionFactory()
        rule = WorkflowTransitionRule(
            transition=transition,
            authorization_type=AuthorizationType.CAPABILITY,
            capability="treasury",
        )

        rule.full_clean()
        rule.save()

        assert rule.capability == "treasury"

    def test_workflow_content_type_is_event(self):
        workflow = WorkflowFactory()

        assert workflow.content_type.model == "event"
        assert workflow.content_type.app_label == "events"
