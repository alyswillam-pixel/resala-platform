from django.db.models import Q

from .models import Committee


def get_presidential_office():
    return Committee.objects.filter(is_presidential_office=True).first()


def is_presidential_office_leader(user) -> bool:
    if not user.is_authenticated:
        return False
    po = get_presidential_office()
    return bool(po) and user.id in (po.director_id, po.vice_director_id)


def get_led_committee(user):
    if not user.is_authenticated:
        return None
    return (
        Committee.objects.filter(is_presidential_office=False)
        .filter(Q(director=user) | Q(vice_director=user))
        .first()
    )
