from rest_framework.permissions import BasePermission

from resala_platform.committees.models import CommitteeCapability
from resala_platform.committees.permissions import committee_has_capability
from resala_platform.committees.permissions import is_presidential_office_leader


def is_event_requester(flow, user):
    return flow.event.requester_id == user.id


def is_treasurer(flow, user):
    if not user.is_authenticated or not getattr(user, "committee_role", None):
        return False

    return committee_has_capability(
        user.committee_role.committee_id,
        CommitteeCapability.Capability.TREASURY,
    )


def is_po_leader(flow, user):
    return is_presidential_office_leader(user)


def is_treasurer_or_po_leader(flow, user):
    return is_treasurer(flow, user) or is_po_leader(flow, user)


class CanCreateEvents(BasePermission):
    message = "Your committee is not authorized to create events."

    def has_permission(self, request, view):
        if request.method != "POST":
            return True

        user = request.user
        if not user.is_authenticated or not getattr(user, "committee_role", None):
            return False

        return committee_has_capability(
            user.committee_role.committee_id,
            CommitteeCapability.Capability.EVENT_CREATION,
        )
