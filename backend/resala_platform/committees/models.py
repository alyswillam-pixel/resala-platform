import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Committee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    name = models.CharField(_("Name"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True)
    director = models.ForeignKey(
        "users.User",
        verbose_name=_("Director"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="directed_committees",
    )
    vice_director = models.ForeignKey(
        "users.User",
        verbose_name=_("Vice Director"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vice_directed_committees",
    )

    is_presidential_office = models.BooleanField(
        _("Is Presidential Office"),
        default=False,
    )

    def clean(self):
        if self.is_presidential_office:
            conflict = Committee.objects.filter(is_presidential_office=True).exclude(
                pk=self.pk,
            )
            if conflict.exists():
                raise ValidationError(
                    _("Only one committee may be the Presidential Office."),
                )

    class Meta:
        verbose_name = _("Committee")
        verbose_name_plural = _("Committees")

    def __str__(self) -> str:
        return self.name


class CommitteeRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    committee = models.ForeignKey(
        Committee,
        verbose_name=_("Committee"),
        on_delete=models.CASCADE,
        related_name="roles",
    )
    name = models.CharField(_("Name"), max_length=100)
    order = models.PositiveIntegerField(_("Order"), null=True, blank=True)

    class Meta:
        verbose_name = _("Committee Role")
        verbose_name_plural = _("Committee Roles")
        unique_together = ("committee", "name")
        ordering = ["committee", "order"]

    def __str__(self) -> str:
        return f"{self.committee.name} — {self.name}"


class CommitteeCapability(models.Model):
    """
    Registry of platform-wide capabilities granted to specific committees.
    Managed exclusively by Presidential Office leadership via the Django admin.
    """

    class Capability(models.TextChoices):
        TREASURY = "treasury", _("Treasury / Budget Approval")
        EVENT_CREATION = "event_creation", _("Event Creation")
        # Future capabilities (e.g., REQUEST_ROUTING) can simply be added here

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    committee = models.ForeignKey(
        "committees.Committee",
        verbose_name=_("Committee"),
        on_delete=models.CASCADE,
        related_name="capabilities",
    )
    capability = models.CharField(
        _("Capability"),
        max_length=50,
        choices=Capability.choices,
    )
    added_at = models.DateTimeField(_("Added At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Committee Capability")
        verbose_name_plural = _("Committee Capabilities")
        unique_together = ("committee", "capability")

    def __str__(self) -> str:
        return f"{self.committee.name} — {self.get_capability_display()}"
