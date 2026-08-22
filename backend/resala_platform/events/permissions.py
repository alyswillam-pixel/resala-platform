from rest_framework.permissions import BasePermission

from resala_platform.committees.models import CommitteeCapability
from resala_platform.committees.permissions import committee_has_capability


class CanCreatedEvents(BasePermission):
    message = "Your committee is not authorized to create events."

    def has_permission(self, request, view):
        if request.method != "POST":
            return True

        user = request.user

        if not user.is_authenticated:
            return False

        committee_role = getattr(user, "committee_role", None)

        if not committee_role:
            return False

        return committee_has_capability(
            committee_role.committee_id,
            CommitteeCapability.Capability.EVENT_CREATION,
        )
