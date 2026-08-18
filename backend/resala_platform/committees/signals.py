from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Committee


def _sync_leadership_staff_status(**kwargs):
    from resala_platform.users.models import User

    is_leader_subquery = Committee.objects.filter(
        Q(director_id=OuterRef("pk")) | Q(vice_director_id=OuterRef("pk")),
    )
    User.objects.filter(is_staff=True, is_superuser=False).annotate(
        is_leader=Exists(is_leader_subquery),
    ).filter(is_leader=False).update(is_staff=False)
    User.objects.filter(is_staff=False).annotate(
        is_leader=Exists(is_leader_subquery),
    ).filter(is_leader=True).update(is_staff=True)


@receiver(post_save, sender=Committee)
def on_committee_save(sender, **kwargs):
    _sync_leadership_staff_status()


@receiver(post_delete, sender=Committee)
def on_committee_delete(sender, **kwargs):
    _sync_leadership_staff_status()
