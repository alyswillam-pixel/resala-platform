import factory
from django.contrib.contenttypes.models import ContentType
from factory.django import DjangoModelFactory

from resala_platform.committees.models import Committee
from resala_platform.committees.models import CommitteeCapability
from resala_platform.committees.models import CommitteeRole
from resala_platform.events.models import Budget
from resala_platform.events.models import Event
from resala_platform.users.models import User
from resala_platform.workflows.models import Workflow
from resala_platform.workflows.models import WorkflowInstance
from resala_platform.workflows.models import WorkflowState
from resala_platform.workflows.models import WorkflowTransition
from resala_platform.workflows.models import WorkflowTransitionAction
from resala_platform.workflows.models import WorkflowTransitionRule


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    name = factory.Sequence(lambda n: f"Test User {n}")
    auc_id = factory.Sequence(lambda n: f"90025{n:04d}")
    auc_email = factory.LazyAttribute(lambda user: f"{user.auc_id}@aucegypt.edu")


class CommitteeFactory(DjangoModelFactory):
    class Meta:
        model = Committee

    name = factory.Sequence(lambda n: f"Committee {n}")
    description = ""


class CommitteeRoleFactory(DjangoModelFactory):
    class Meta:
        model = CommitteeRole

    committee = factory.SubFactory(CommitteeFactory)
    name = factory.Sequence(lambda n: f"Role {n}")


class CommitteeCapabilityFactory(DjangoModelFactory):
    class Meta:
        model = CommitteeCapability

    committee = factory.SubFactory(CommitteeFactory)
    capability = CommitteeCapability.Capability.TREASURY


class PresidentialOfficeFactory(CommitteeFactory):
    is_presidential_office = True


class TreasuryCommitteeFactory(CommitteeFactory):
    name = factory.Sequence(lambda n: f"Treasury {n}")


class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event

    title = factory.Sequence(lambda n: f"Test Event {n}")
    description = {}
    requester = factory.SubFactory(UserFactory)


class BudgetFactory(DjangoModelFactory):
    class Meta:
        model = Budget

    event = factory.SubFactory(EventFactory)
    amount = "10000.00"


class WorkflowFactory(DjangoModelFactory):
    class Meta:
        model = Workflow

    name = factory.Sequence(lambda n: f"Workflow {n}")
    description = ""
    content_type = factory.LazyAttribute(
        lambda _: ContentType.objects.get_for_model(Event),
    )
    created_by = factory.SubFactory(UserFactory)
    is_active = False


class WorkflowStateFactory(DjangoModelFactory):
    class Meta:
        model = WorkflowState

    workflow = factory.SubFactory(WorkflowFactory)
    name = factory.Sequence(lambda n: f"State {n}")
    description = ""
    is_initial = False
    is_terminal = False
    review_committee = None


class InitialWorkflowStateFactory(WorkflowStateFactory):
    is_initial = True


class TerminalWorkflowStateFactory(WorkflowStateFactory):
    is_terminal = True


class WorkflowTransitionFactory(DjangoModelFactory):
    class Meta:
        model = WorkflowTransition

    workflow = factory.SubFactory(WorkflowFactory)
    name = factory.Sequence(lambda n: f"Transition {n}")
    description = ""
    source = factory.SubFactory(
        WorkflowStateFactory,
        workflow=factory.SelfAttribute("..workflow"),
    )
    target = factory.SubFactory(
        WorkflowStateFactory,
        workflow=factory.SelfAttribute("..workflow"),
    )


class WorkflowTransitionRuleFactory(DjangoModelFactory):
    class Meta:
        model = WorkflowTransitionRule

    transition = factory.SubFactory(WorkflowTransitionFactory)
    authorization_type = "requester"
    capability = ""
    committee = None


class CapabilityTransitionRuleFactory(WorkflowTransitionRuleFactory):
    authorization_type = "capability"
    capability = CommitteeCapability.Capability.TREASURY


class CommitteeMemberTransitionRuleFactory(WorkflowTransitionRuleFactory):
    authorization_type = "committee_member"
    committee = factory.SubFactory(CommitteeFactory)


class CommitteeLeaderTransitionRuleFactory(WorkflowTransitionRuleFactory):
    authorization_type = "committee_leader"
    committee = factory.SubFactory(CommitteeFactory)


class PresidentialOfficeLeaderRuleFactory(WorkflowTransitionRuleFactory):
    authorization_type = "presidential_office_leader"


class WorkflowTransitionActionFactory(DjangoModelFactory):
    class Meta:
        model = WorkflowTransitionAction

    transition = factory.SubFactory(WorkflowTransitionFactory)
    action_type = "set_budget_status"
    value = "Approved"
    order = 0


class WorkflowInstanceFactory(DjangoModelFactory):
    class Meta:
        model = WorkflowInstance

    workflow = factory.SubFactory(WorkflowFactory)
    current_state = factory.SubFactory(
        WorkflowStateFactory,
        workflow=factory.SelfAttribute("..workflow"),
    )
    content_object = factory.SubFactory(EventFactory)

    @factory.post_generation
    def align_content_type(self, create, extracted, **kwargs):
        if not create:
            return

        content_type = ContentType.objects.get_for_model(self.content_object)

        if self.workflow.content_type_id != content_type.id:
            self.workflow.content_type = content_type
            self.workflow.save(update_fields=["content_type"])

        self.content_type = content_type
        self.object_id = self.current_state.pk
        self.save(update_fields=["content_type", "object_id"])
