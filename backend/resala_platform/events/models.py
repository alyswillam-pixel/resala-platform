import uuid
from decimal import Decimal

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _

from resala_platform.workflows.models import WorkflowInstance


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

    created_at = models.DateField(_("Created At"), auto_now_add=True)
    updated_at = models.DateField(_("Updated At"), auto_now=True)

    workflow_instance = GenericRelation(
        WorkflowInstance,
        related_query_name="events",
    )

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


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
        default=Decimal("0.0"),
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

    def __str__(self) -> str:
        return f"Budget for {self.event.title} — {self.amount}"
