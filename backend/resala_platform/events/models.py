import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    requester = models.ForeignKey(
        "users.User",
        verbose_name=_("Requester"),
        on_delete=models.PROTECT,
        related_name="requested_events",
    )
    # Using FSMField for predictable state management
    current_state = FSMField(_("Current State"), default="Draft", protected=True)
    
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    # --- Event & Budget Workflows (per ADR 0006) ---
    
    @transition(field=current_state, source="Draft", target="Pending Treasurer Review")
    def submit_for_budget_review(self):
        pass

    @transition(field=current_state, source="Pending Treasurer Review", target="Budget Approved")
    def treasurer_approve_budget(self):
        pass

    @transition(field=current_state, source="Pending Treasurer Review", target="Pending Presidential Review")
    def treasurer_escalate_budget(self):
        pass

    @transition(field=current_state, source="Pending Presidential Review", target="Budget Approved")
    def president_approve_budget(self):
        pass

    @transition(field=current_state, source=["Pending Treasurer Review", "Pending Presidential Review"], target="Budget Rejected")
    def reject_budget(self):
        pass

    @transition(field=current_state, source="Budget Rejected", target="Draft")
    def revise_budget(self):
        pass

    @transition(field=current_state, source="Budget Rejected", target="Turned Down")
    def turn_down_event(self):
        pass

    @transition(field=current_state, source="Budget Approved", target="Active")
    def activate_event(self):
        pass

    @transition(field=current_state, source="Active", target="Done")
    def complete_event(self):
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


class Request(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    event = models.ForeignKey(
        Event,
        verbose_name=_("Event"),
        on_delete=models.CASCADE,
        related_name="requests",
    )
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    requester = models.ForeignKey(
        "users.User",
        verbose_name=_("Requester"),
        on_delete=models.PROTECT,
        related_name="submitted_requests",
    )
    committee = models.ForeignKey(
        "committees.Committee",
        verbose_name=_("Committee"),
        on_delete=models.PROTECT,
        related_name="requests",
    )
    assigned_to = models.ForeignKey(
        "users.User",
        verbose_name=_("Assigned To"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_requests",
    )
    current_state = FSMField(_("Current State"), default="Draft", protected=True)
    
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Request")
        verbose_name_plural = _("Requests")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.committee.name})"

    # --- Standard Request Workflows ---
    
    @transition(field=current_state, source="Draft", target="Submitted")
    def submit_request(self):
        pass

    @transition(field=current_state, source="Submitted", target="Under Review")
    def begin_review(self):
        pass

    @transition(field=current_state, source="Under Review", target="Approved")
    def approve_request(self):
        pass

    @transition(field=current_state, source="Under Review", target="Rejected")
    def reject_request(self):
        pass


class RequestStateTransition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    request = models.ForeignKey(
        Request,
        verbose_name=_("Request"),
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
        related_name="request_transitions_made",
    )
    note = models.TextField(_("Note"), blank=True)
    
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Request State Transition")
        verbose_name_plural = _("Request State Transitions")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.request.title}: {self.from_state} -> {self.to_state}"


class RequestAssignmentHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    request = models.ForeignKey(
        Request,
        verbose_name=_("Request"),
        on_delete=models.CASCADE,
        related_name="assignment_history",
    )
    assigned_to = models.ForeignKey(
        "users.User",
        verbose_name=_("Assigned To"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="assignment_received_history",
    )
    assigned_by = models.ForeignKey(
        "users.User",
        verbose_name=_("Assigned By"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="assignment_given_history",
    )
    
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Request Assignment History")
        verbose_name_plural = _("Request Assignment Histories")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.request.title} assigned to {self.assigned_to}"


class RequestEscalation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    request = models.ForeignKey(
        Request,
        verbose_name=_("Request"),
        on_delete=models.CASCADE,
        related_name="escalations",
    )
    raised_by = models.ForeignKey(
        "users.User",
        verbose_name=_("Raised By"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="raised_escalations",
    )
    reason_category = models.CharField(_("Reason Category"), max_length=100)
    description = models.TextField(_("Description"))
    
    # Using FSMField for escalation workflows (per ADR 0008)
    status = FSMField(_("Status"), default="Open", protected=True)
    
    handled_by = models.ForeignKey(
        "users.User",
        verbose_name=_("Handled By"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="handled_escalations",
    )
    resolution_note = models.TextField(_("Resolution Note"), blank=True)
    
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    resolved_at = models.DateTimeField(_("Resolved At"), null=True, blank=True)

    class Meta:
        verbose_name = _("Request Escalation")
        verbose_name_plural = _("Request Escalations")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Escalation for {self.request.title} - {self.status}"

    # --- Request Escalation Workflows (per ADR 0008) ---
    
    @transition(field=status, source="Open", target="In Review")
    def review_escalation(self):
        pass

    @transition(field=status, source="In Review", target="Resolved")
    def resolve_escalation(self):
        pass

    @transition(field=status, source="In Review", target="Dismissed")
    def dismiss_escalation(self):
        pass