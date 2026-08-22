import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from resala_platform.committees.models import Committee
from resala_platform.committees.models import CommitteeCapability
from resala_platform.users.models import User


class Workflow(models.Model):
    """
    A configurable workflow definition.

    A workflow describes the states and transitions that an object can move
    through. It contains no runtime state itself.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    name = models.CharField(_("Name"), max_length=150)
    description = models.TextField(_("Description"), blank=True)

    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_("Content Type"),
        on_delete=models.PROTECT,
        related_name="workflows",
    )

    is_active = models.BooleanField(_("Active"), default=False)
    created_by = models.ForeignKey(
        User,
        verbose_name=_("Created By"),
        on_delete=models.PROTECT,
        related_name="created_workflows",
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Workflow")
        verbose_name_plural = _("Workflows")
        ordering = ["name"]

    def clean(self):
        if self.is_active:
            conflict = Workflow.objects.filter(
                content_type=self.content_type,
                is_active=True,
            ).exclude(pk=self.pk)

            if conflict.exists():
                raise ValidationError(
                    _("Only one active workflow exist for each content type."),
                )

    def __str__(self) -> str:
        return self.name


class WorkflowState(models.Model):
    """
    A state belonging to a workflow definition.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    workflow = models.ForeignKey(
        Workflow,
        verbose_name=_("Workflow"),
        on_delete=models.CASCADE,
        related_name="states",
    )
    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    is_initial = models.BooleanField(_("Initial"), default=False)
    is_terminal = models.BooleanField(_("Terminal"), default=False)
    review_committee = models.ForeignKey(
        Committee,
        verbose_name=_("Review Committee"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="workflow_review_states",
    )

    class Meta:
        verbose_name = _("Workflow State")
        verbose_name_plural = _("Workflow States")
        ordering = ["workflow", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["workflow", "name"],
                name="unique_workflow_state_name",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.workflow.name} — {self.name}"


class WorkflowTransition(models.Model):
    """
    A directed edge between two states.

    The transition itself does not contain Python permission functions.
    Authorization is represented by WorkflowTransitionRule rows.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    workflow = models.ForeignKey(
        Workflow,
        verbose_name=_("Workflow"),
        on_delete=models.CASCADE,
        related_name="transitions",
    )
    name = models.CharField(_("Name"), max_length=150)
    description = models.TextField(_("Description"), blank=True)

    source = models.ForeignKey(
        WorkflowState,
        verbose_name=_("Source"),
        on_delete=models.CASCADE,
        related_name="outgoing_transitions",
    )
    target = models.ForeignKey(
        WorkflowState,
        verbose_name=_("Target"),
        on_delete=models.CASCADE,
        related_name="incoming_transitions",
    )

    class Meta:
        verbose_name = _("Workflow Transition")
        verbose_name_plural = _("Workflow Transitions")
        ordering = ["workflow", "name"]

    def clean(self):
        if self.source_id and self.target_id:
            if self.source.workflow_id != self.workflow_id:
                raise ValidationError(
                    _("The source state must belong to this workflow."),
                )

            if self.target.workflow_id != self.workflow_id:
                raise ValidationError(
                    _("The target state must belong to this workflow."),
                )

    def __str__(self):
        return f"{self.workflow.name}: {self.source.name} --> {self.target.name}"


class AuthorizationType(models.TextChoices):
    REQUESTER = "requester", _("Requester")
    CAPABILITY = "capability", _("Committee Capability")
    COMMITTEE_MEMBER = "committee_member", _("Committee Member")
    COMMITTEE_LEADER = "committee_leader", _("Committee Leader")
    PRESIDENTIAL_OFFICE_LEADER = (
        "presidential_office_leader",
        _("Presidential Office Leader"),
    )


class WorkflowTransitionRule(models.Model):
    """
    Define who may excute a transition.
    Multiple rules are ORed together

    Example:
        Transition: Approve Budget

        Rule 1:
            type = CAPABILITY
            capability = TREASURY

        Rule 2:
            type = PRESIDENTIAL_OFFICE_LEADER

    means either a treasury-capable committee member or a PO leader may execute
    the transition.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    transition = models.ForeignKey(
        WorkflowTransition,
        verbose_name=_("Transition"),
        on_delete=models.CASCADE,
        related_name="rules",
    )
    authorization_type = models.CharField(
        _("Authorization Type"),
        max_length=50,
        choices=AuthorizationType,
    )
    capability = models.CharField(
        _("Capability"),
        max_length=50,
        blank=True,
        choices=CommitteeCapability.Capability.choices,
    )
    committee = models.ForeignKey(
        Committee,
        verbose_name=_("Committee"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="workflow_authorization_rules",
    )

    class Meta:
        verbose_name = _("Workflow Transition Rule")
        verbose_name_plural = _("Workflow Transition Rules")

    def clean(self):
        if self.authorization_type == AuthorizationType.CAPABILITY:
            if not self.capability:
                raise ValidationError(
                    _("A capability is required for a capability rule."),
                )

        if self.authorization_type in {
            AuthorizationType.COMMITTEE_LEADER,
            AuthorizationType.COMMITTEE_MEMBER,
        }:
            if not self.committee_id:
                raise ValidationError(
                    _("A committee is required for this authorization rule."),
                )

    def __str__(self):
        return f"{self.transition.name} — {self.get_authorization_type_display()}"


class WorkflowActionType(models.TextChoices):
    SET_BUDGET_STATUS = "set_update_status", _("Set Budget Status")
    SET_BUDGET_APPROVER = "set_budget_approver", _("Set Budget Approver")
    CLEAR_BUDGET_APPROVER = ("clear_budget_approver", _("Clear Budget Approver"))


class WorkflowTransitionAction(models.Model):
    """
    A controlled side effect executed when a transition succeeds.
    The value is interpreted according to the action type.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    transition = models.ForeignKey(
        WorkflowTransition,
        verbose_name=_("Transition"),
        on_delete=models.CASCADE,
        related_name="actions",
    )
    action_type = models.CharField(
        _("Action Type"),
        max_length=50,
        choices=WorkflowActionType,
    )
    value = models.CharField(_("Value"), max_length=100, blank=True)
    order = models.PositiveIntegerField(_("Order"), default=0)

    class Meta:
        verbose_name = _("Workflow Transition Action")
        verbose_name_plural = _("Workflow Transition Actions")
        ordering = ["transition", "order"]

    def __str__(self) -> str:
        return f"{self.transition.name} — {self.get_action_type_display()}"


class WorkflowInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    workflow = models.ForeignKey(
        Workflow,
        verbose_name=_("Workflow"),
        on_delete=models.PROTECT,
        related_name="instances",
    )
    current_state = models.ForeignKey(
        WorkflowState,
        verbose_name=_("Current State"),
        on_delete=models.PROTECT,
        related_name="instances",
    )
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_("Content Type"),
        on_delete=models.PROTECT,
    )

    object_id = models.UUIDField(_("Object ID"))
    content_object = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Workflow Instance")
        verbose_name_plural = _("Workflow Instances")
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id"],
                name="unique_workflow_instance_per_object",
            ),
        ]

    def clean(self):
        if self.current_state.workflow_id != self.workflow_id:
            raise ValidationError(
                _("The current state must belong to the selected workflow."),
            )

        if self.content_type_id != self.workflow.content_type_id:
            raise ValidationError(
                _("The workflow does not apply to this content type."),
            )

    def __str__(self) -> str:
        return f"{self.workflow.name} — {self.current_state.name}"


class WorkflowTransitionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    instance = models.ForeignKey(
        WorkflowInstance,
        verbose_name=_("Workflow Instance"),
        on_delete=models.CASCADE,
        related_name="transition_logs",
    )
    transition = models.ForeignKey(
        WorkflowTransition,
        verbose_name=_("Transition"),
        on_delete=models.PROTECT,
        related_name="logs",
    )
    from_state = models.ForeignKey(
        WorkflowState,
        verbose_name=_("From State"),
        on_delete=models.PROTECT,
        related_name="+",
    )
    to_state = models.ForeignKey(
        WorkflowState,
        verbose_name=_("To State"),
        on_delete=models.PROTECT,
        related_name="+",
    )
    actor = models.ForeignKey(
        User,
        verbose_name=_("Actor"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="workflow_transitions_made",
    )
    note = models.TextField(_("Note"), blank=True)

    created_at = models.DateField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Workflow Transition Log")
        verbose_name_plural = _("Workflow Transition Logs")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.instance}: {self.from_state.name} --> {self.to_state.name}"
