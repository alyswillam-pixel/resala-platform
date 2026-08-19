import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from resala_platform.events.models import Event, EventStateTransition, Budget
from resala_platform.committees.tests.factories import (
    CommitteeFactory, 
    CommitteeRoleFactory, 
    PresidentialOfficeCommitteeFactory
)

pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def requester(django_user_model):
    return django_user_model.objects.create_user(
        auc_email="req@aucegypt.edu", auc_id="900260001", password="pw"
    )

@pytest.fixture
def treasurer(django_user_model):
    committee = CommitteeFactory(name="Treasury")
    role = CommitteeRoleFactory(name="Treasurer", committee=committee)
    return django_user_model.objects.create_user(
        auc_email="treasurer@aucegypt.edu", auc_id="900260002", password="pw", committee_role=role
    )

@pytest.fixture
def po_leader(django_user_model):
    po = PresidentialOfficeCommitteeFactory()
    leader = django_user_model.objects.create_user(
        auc_email="po@aucegypt.edu", auc_id="900260003", password="pw"
    )
    po.director = leader
    po.save()
    leader.refresh_from_db()
    return leader

@pytest.fixture
def event(requester):
    evt = Event.objects.create(title="Test Event", requester=requester)
    Budget.objects.create(event=evt, amount=500.00)
    return evt

def test_event_workflow_success_and_audit_trail(api_client, event, requester, treasurer):
    # 1. Requester submits event successfully
    api_client.force_authenticate(user=requester)
    url = reverse("api:event-submit-for-budget-review", kwargs={"pk": event.pk})
    response = api_client.post(url)
    
    assert response.status_code == status.HTTP_200_OK
    
    event = Event.objects.get(pk=event.pk)
    assert event.current_state == "Pending Treasurer Review"
    assert event.budget.status == "Pending Treasurer Review"
    
    # Audit trail verifies actor (Use .first() because ordering is -created_at)
    transition = EventStateTransition.objects.first()
    assert transition.event == event
    assert transition.action == "submit_for_budget_review"
    assert transition.actor == requester
    
    # 2. Treasurer successfully approves
    api_client.force_authenticate(user=treasurer)
    url_approve = reverse("api:event-treasurer-approve-budget", kwargs={"pk": event.pk})
    resp_approve = api_client.post(url_approve)
    
    assert resp_approve.status_code == status.HTTP_200_OK
    
    event = Event.objects.get(pk=event.pk)
    assert event.current_state == "Budget Approved"
    
    # Verifies the Budget object status was actively synced
    assert event.budget.status == "Approved"
    assert event.budget.approved_by == treasurer
    
    # Audit trail verifies treasurer
    transition2 = EventStateTransition.objects.first()
    assert transition2.action == "treasurer_approve_budget"
    assert transition2.actor == treasurer

def test_unauthorized_fsm_transition_blocked(api_client, event, treasurer):
    # A Treasurer attempts to submit an event on behalf of the requester
    api_client.force_authenticate(user=treasurer)
    url = reverse("api:event-submit-for-budget-review", kwargs={"pk": event.pk})
    response = api_client.post(url)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    event = Event.objects.get(pk=event.pk)
    assert event.current_state == "Draft" 

def test_invalid_fsm_sequence_blocked(api_client, event, requester):
    # A Requester tries to activate an event before budget approval
    api_client.force_authenticate(user=requester)
    url = reverse("api:event-activate-event", kwargs={"pk": event.pk})
    response = api_client.post(url)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST