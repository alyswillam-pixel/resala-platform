from resala_platform.committees.permissions import is_presidential_office_leader

from .models import TreasuryCommittee


def is_event_requester(flow, user):
    return flow.event.requester_id == user.id


def is_treasurer(flow, user):
    if not user.is_authenticated or not getattr(user, "committee_role", None):
        return False

    return TreasuryCommittee.objects.filter(
        committee_id=user.committee_role.committee_id,
    ).exists()


def is_po_leader(flow, user):
    return is_presidential_office_leader(user)


def is_treasurer_or_po_leader(flow, user):
    return is_treasurer(flow, user) or is_po_leader(flow, user)
