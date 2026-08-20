import uuid
from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _


class EventState(models.TextChoices):
    DRAFT = "Draft", _("Draft")
    PENDING_TREASURER_REVIEW = "Pending Treasurer Review", _("Pending Treasurer Review")
    PENDING_PRESIDENTIAL_REVIEW = (
        "Pending Presidential Review",
        _(
            "Pending Presidential Review",
        ),
    )
    BUDGET_APPROVED = "Budget Approved", _("Budget Approved")
    ACTIVE = "Active", _("Active")
    COMPLETED = "Completed", _("Completed")
    BUDGET_REJECTED = "Budget Rejected", _("Budget Rejected")
    TURNED_DOWN = "Turned Down", _("Turned Down")


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    title = models.CharField(_("Title"), max_length=255)
    description = models.JSONField(_("Description"), blank=True, default=dict)
    requester = models.ForeignKey(
        "users.User",
        verbose_name=_("Requester"),
        on_delete=models.PROTECT,
        related_name="requested_events",
    )
    current_state = models.CharField(
        _("Current State"),
        max_length=50,
        choices=EventState,
        default=EventState.DRAFT,
    )
    created_at = models.DateField(_("Created At"), auto_now_add=True)
    updated_at = models.DateField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class EventStateTransition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    event = models.ForeignKey(
        Event,
        verbose_name=_("Event"),
        on_delete=models.CASCADE,
        related_name="state_transitions",
    )
    from_state = models.CharField(_("From State"), max_length=50)
    to_state = models.CharField(_("To State"), max_length=50)
    action = models.CharField(_("Action"), max_length=100)
    actor = models.ForeignKey(
        "users.User",
        verbose_name=_("Actor"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="event_transitions_made",
    )
    note = models.TextField(_("Note"), blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Event State Transition")
        verbose_name_plural = _("Event State Transitions")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event.title}: {self.from_state} -> {self.to_state}"


class Budget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    event = models.OneToOneField(
        Event,
        verbose_name=_("Event"),
        on_delete=models.CASCADE,
        related_name="budget",
    )
    amount = models.DecimalField(
        _("Amount"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    status = models.CharField(_("State"), max_length=50, default="Pending")
    approved_by = models.ForeignKey(
        "users.User",
        verbose_name=_("Approved By"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_budgets",
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Budget")
        verbose_name_plural = _("Budgets")

    def __str__(self):
        return f"Budget for {self.event.title} — {self.amount}"
