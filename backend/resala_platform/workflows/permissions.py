from rest_framework.permissions import BasePermission

from resala_platform.committees.permissions import is_presidential_office_leader


class IsPresidentialOfficeLeader(BasePermission):
    message = "Only Presidential Office leadership can configure workflows."

    def has_permission(self, request, view):
        return is_presidential_office_leader(request.user)
