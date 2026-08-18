from django.contrib import admin
from django.core.exceptions import PermissionDenied

from .models import Committee
from .models import CommitteeRole
from .permissions import get_led_committee
from .permissions import is_presidential_office_leader


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "director",
        "vice_director",
        "is_presidential_office",
    )
    search_fields = ("name",)

    def _allowed(self, request, obj=None):
        return request.user.is_superuser or is_presidential_office_leader(request.user)

    has_module_permission = has_view_permission = _allowed
    has_add_permission = has_change_permission = has_delete_permission = _allowed


@admin.register(CommitteeRole)
class CommitteeRoleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "committee",
        "order",
    )
    list_filter = ("committee",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or is_presidential_office_leader(request.user):
            return qs
        led = get_led_committee(request.user)
        return qs.filter(committee=led) if led else qs.none()

    def has_module_permission(self, request, obj=None):
        return (
            request.user.is_superuser
            or is_presidential_office_leader(request.user)
            or get_led_committee(request.user) is not None
        )

    has_view_permission = has_add_permission = has_module_permission

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or is_presidential_office_leader(request.user):
            return True
        led = get_led_committee(request.user)
        return bool(led) and (obj is None or obj.committee_id == led.id)

    has_delete_permission = has_change_permission

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "committee" and not (
            request.user.is_superuser or is_presidential_office_leader(request.user)
        ):
            led = get_led_committee(request.user)
            kwargs["queryset"] = (
                Committee.objects.filter(pk=led.pk) if led else Committee.objects.none()
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not (
            request.user.is_superuser or is_presidential_office_leader(request.user)
        ):
            led = get_led_committee(request.user)
            if not led or obj.committee_id != led.id:
                raise PermissionDenied(
                    "You may only manage roles for your own committee.",
                )

        super().save_model(request, obj, form, change)
