import pytest
from django.contrib import admin
from django.test import RequestFactory

from resala_platform.committees.models import CommitteeCapability
from resala_platform.workflows.admin import WorkflowTransitionRuleAdmin
from resala_platform.workflows.models import AuthorizationType
from resala_platform.workflows.models import WorkflowTransitionRule
from resala_platform.workflows.tests.factories import WorkflowTransitionRuleFactory

pytestmark = pytest.mark.django_db


class TestWorkflowTransitionRuleAdmin:
    def setup_method(self):
        self.factory = RequestFactory()
        self.site = admin.AdminSite()

    def test_capability_field_is_a_select(self):
        rule = WorkflowTransitionRuleFactory()
        request = self.factory.get("/admin/workflows/workflowtransitionrule/add/")
        model_admin = WorkflowTransitionRuleAdmin(WorkflowTransitionRule, self.site)
        form_class = model_admin.get_form(request, obj=rule)
        form = form_class()
        field = form.fields["capability"]

        assert field.choices is not None
        assert (
            CommitteeCapability.Capability.TREASURY,
            "Treasury / Budget Approval",
        ) in field.choices

        assert (
            CommitteeCapability.Capability.EVENT_CREATION,
            "Event Creation",
        ) in field.choices

    def test_authorization_type_is_a_select(self):
        rule = WorkflowTransitionRuleFactory()
        request = self.factory.get("/admin/workflows/workflowtransitionrule/add/")
        model_admin = WorkflowTransitionRuleAdmin(WorkflowTransitionRule, self.site)
        form_class = model_admin.get_form(request, obj=rule)
        form = form_class()
        field = form.fields["authorization_type"]

        assert field.choices is not None
        assert (
            AuthorizationType.CAPABILITY,
            "Committee Capability",
        ) in field.choices
        assert (
            AuthorizationType.REQUESTER,
            "Requester",
        ) in field.choices
