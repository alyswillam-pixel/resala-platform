import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition

from resala_platform.committees.permissions import is_presidential_office_leader

# --- Permission Helper Functions ---

def is_event_requester(instance, user):
    return instance.requester == user

def is_treasurer(instance, user):
    # Strict null-checking for both the role AND the committee relation
    if not user.is_authenticated or not getattr(user, 'committee_role', None) or not user.committee_role.committee:
        return False
    return 'treasurer' in user.committee_role.name.lower() or 'treasury' in user.committee_role.committee.name.lower()

def is_po_leader(instance, user):
    return is_presidential_office_leader(user)

def is_treasurer_or_po_leader(instance, user):
    return is_treasurer(instance, user) or is_po_leader(instance, user)


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
    current_state = FSMField(_("Current State"), default="Draft", protected=True)
    
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    # --- Event & Budget Workflows ---
    
    @transition(field=current_state, source="Draft", target="Pending Treasurer Review", permission=is_event_requester)
    def submit_for_budget_review(self, by_user=None):
        if hasattr(self, 'budget'):
            self.budget.status = 'Pending Treasurer Review'
            self.budget.save()

    @transition(field=current_state, source="Pending Treasurer Review", target="Budget Approved", permission=is_treasurer)
    def treasurer_approve_budget(self, by_user=None):
        if hasattr(self, 'budget'):
            self.budget.status = 'Approved'
            self.budget.approved_by = by_user
            self.budget.save()

    @transition(field=current_state, source="Pending Treasurer Review", target="Pending Presidential Review", permission=is_treasurer)
    def treasurer_escalate_budget(self, by_user=None):
        if hasattr(self, 'budget'):
            self.budget.status = 'Pending Presidential Review'
            self.budget.save()

    @transition(field=current_state, source="Pending Presidential Review", target="Budget Approved", permission=is_po_leader)
    def president_approve_budget(self, by_user=None):
        if hasattr(self, 'budget'):
            self.budget.status = 'Approved'
            self.budget.approved_by = by_user
            self.budget.save()

    @transition(field=current_state, source=["Pending Treasurer Review", "Pending Presidential Review"], target="Budget Rejected", permission=is_treasurer_or_po_leader)
    def reject_budget(self, by_user=None):
        if hasattr(self, 'budget'):
            self.budget.status = 'Rejected'
            self.budget.save()

    @transition(field=current_state, source="Budget Rejected", target="Draft", permission=is_event_requester)
    def revise_budget(self, by_user=None):
        if hasattr(self, 'budget'):
            self.budget.status = 'Pending'
            self.budget.approved_by = None
            self.budget.save()

    @transition(field=current_state, source="Budget Rejected", target="Turned Down", permission=is_treasurer_or_po_leader)
    def turn_down_event(self, by_user=None):
        pass # Event is turned down, budget remains rejected

    @transition(field=current_state, source="Budget Approved", target="Active", permission=is_event_requester)
    def activate_event(self, by_user=None):
        pass

    @transition(field=current_state, source="Active", target="Completed", permission=is_event_requester)
    def complete_event(self, by_user=None):
        pass


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

    def __str__(self) -> str:
        return f"{self.event.title}: {self.from_state} -> {self.to_state}"


class Budget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    event = models.OneToOneField(
        Event,
        verbose_name=_("Event"),
        on_delete=models.CASCADE,
        related_name="budget",
    )
    amount = models.DecimalField(_("Amount"), max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(_("Status"), max_length=50, default="Pending")
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
        return f"Budget for {self.event.title} - {self.amount}"