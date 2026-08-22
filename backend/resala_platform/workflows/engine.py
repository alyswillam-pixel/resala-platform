from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from resala_platform.committees.permissions import committee_has_capability
from resala_platform.committees.permissions import is_presidential_office_leader

from .models import AuthorizationType
from .models import Workflow
from .models import WorkflowActionType
from .models import WorkflowInstance
from .models import WorkflowState
from .models import WorkflowTransition
from .models import WorkflowTransitionLog


class WorkflowError(Exception):
    """Base exception for workflow execution errors."""


class InvalidTransitionError(WorkflowError):
    pass


class UnAuthorizedTransitionError(WorkflowError):
    pass


class WorkflowEngine:
    """
    Generic runtime engine for database-defined workflows.
    """

    def __init__(self, instance: WorkflowInstance):
        self.instance = instance

    @property
    def state(self) -> WorkflowState:
        return self.instance.current_state

    def available_transitions(self, user):
        transitions = self.state.outgoing_transitions.filter(
            workflow=self.instance.workflow,
        ).prefetch_related("rules", "actions")

        return [
            transition
            for transition in transitions
            if self.can_execute(transition, user)
        ]

    def can_execute(self, transition, user) -> bool:
        if transition.workflow_id != self.instance.workflow_id:
            return False

        if transition.source_id != self.instance.current_state_id:
            return False

        rules = list(transition.rules.all())

        if not rules:
            return False

        return any(self._check_rule(rule, user) for rule in rules)

    def _check_rule(self, rule, user) -> bool:  # noqa: PLR0911
        if not user.is_authenticated:
            return False

        if rule.authorization_type == AuthorizationType.REQUESTER:
            return (
                getattr(self.instance.content_object, "requester_id", None) == user.id
            )

        if rule.authorization_type == AuthorizationType.CAPABILITY:
            committee_role = getattr(user, "committee_role", None)

            if not committee_role:
                return False

            return committee_has_capability(
                committee_role.committee_id,
                rule.capability,
            )

        if rule.authorization_type == AuthorizationType.COMMITTEE_MEMBER:
            committee_role = getattr(user, "committee_role", None)

            return bool(
                committee_role and committee_role.committee_id == rule.committee_id,
            )

        if rule.authorization_type == AuthorizationType.COMMITTEE_LEADER:
            if not rule.committee_id:
                return False

            return user.id in {
                rule.committee.director_id,
                rule.committee.vice_director_id,
            }

        if rule.authorization_type == AuthorizationType.PRESIDENTIAL_OFFICE_LEADER:
            return is_presidential_office_leader(user)

        return False

    @transaction.atomic
    def execute(self, transition: WorkflowTransition, user, note: str = ""):
        self.instance = (
            WorkflowInstance.objects.select_for_update()
            .select_related("workflow", "current_state", "content_type")
            .get(pk=self.instance.pk)
        )

        transition = (
            WorkflowTransition.objects.select_for_update()
            .prefetch_related("rules", "actions")
            .select_related("source", "target", "workflow")
            .get(pk=transition.pk)
        )

        if transition.workflow_id != self.instance.workflow_id:
            raise InvalidTransitionError(
                "This transition does not belong to the instance workflow.",
            )

        if transition.source_id != self.instance.current_state_id:
            raise InvalidTransitionError(
                "This transition is not available from the current state",
            )

        if not self.can_execute(transition, user):
            raise UnAuthorizedTransitionError(
                "You are not authorized to perform this transition.",
            )

        old_state = self.instance.current_state
        target_state = transition.target

        self._execute_actions(transition=transition, actor=user)

        self.instance.current_state = target_state
        self.instance.save(update_fields=["current_state", "updated_at"])

        WorkflowTransitionLog.objects.create(
            instance=self.instance,
            transition=transition,
            from_state=old_state,
            to_state=target_state,
            actor=user,
            note=note,
        )

        return self.instance

    def _execute_actions(self, transition, actor):
        obj = self.instance.content_object

        for action in transition.actions.all():
            if action.action_type == WorkflowActionType.SET_BUDGET_STATUS:
                self._set_budget_status(obj, action.value)
            elif action.action_type == WorkflowActionType.SET_BUDGET_APPROVER:
                self._set_budget_approver(obj, actor)
            elif action.action_type == WorkflowActionType.CLEAR_BUDGET_APPROVER:
                self._clear_budget_approver(obj)
            else:
                raise WorkflowError(
                    f"Unsupported workflow action: {action.action_type}",
                )

    @staticmethod
    def _set_budget_status(obj, value):
        budget = getattr(obj, "budget", None)

        if budget is None:
            raise WorkflowError(
                "This workflow action requires the object to have a budget.",
            )

        budget.status = value
        budget.save(update_fields=["status", "updated_at"])

    @staticmethod
    def _set_budget_approver(obj, actor):
        budget = getattr(obj, "budget", None)

        if budget is None:
            raise WorkflowError(
                "This workflow action requires the object to have a budget.",
            )

        budget.approved_by = actor
        budget.save(update_fields=["approved_by", "updated_at"])

    @staticmethod
    def _clear_budget_approver(obj):
        budget = getattr(obj, "budget", None)

        if budget is None:
            raise WorkflowError(
                "This workflow action requires the object to have a budget.",
            )

        budget.approved_by = None
        budget.save(update_fields=["approved_by", "updated_at"])


class WorkflowService:
    """
    Created workflow instances for domain objects.
    """

    @staticmethod
    @transaction.atomic
    def start(obj, workflow: Workflow) -> WorkflowInstance:
        content_type = ContentType.objects.get_for_model(obj)

        if content_type != workflow.content_type:
            raise WorkflowError("This workflow does not apply to this object.")

        initial_state = workflow.states.filter(is_initial=True).first()

        if initial_state is None:
            raise WorkflowError("The workflow does not have an initial state.")

        instance, created = WorkflowInstance.objects.get_or_create(
            content_type=content_type,
            object_id=obj.pk,
            defaults={
                "workflow": workflow,
                "current_state": initial_state,
            },
        )

        if not created:
            raise WorkflowError("This object already has a workflow instance.")

        return instance
