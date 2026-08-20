from django.contrib import admin
from django.core.exceptions import PermissionDenied

from .models import Committee
from .models import CommitteeCapability
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

    def get_object(self, request, object_id, from_field=None):
        # Try the scoped queryset first (covers the normal case).
        obj = super().get_object(request, object_id, from_field)
        if obj is not None:
            return obj
        # Fall back to the unfiltered queryset so that existing-but-forbidden
        # objects are returned and properly rejected by has_*_permission (403)
        # instead of silently treated as "not found" (302 redirect).
        model = self.model
        try:
            pk = model._meta.pk.get_prep_value(object_id)
            return model._default_manager.get(pk=pk)
        except model.DoesNotExist, ValueError:
            return None

    def has_module_permission(self, request, obj=None):
        return (
            request.user.is_superuser
            or is_presidential_office_leader(request.user)
            or get_led_committee(request.user) is not None
        )

    has_add_permission = has_module_permission

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser or is_presidential_office_leader(request.user):
            return True
        led = get_led_committee(request.user)
        return bool(led) and (obj is None or obj.committee_id == led.id)

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


@admin.register(CommitteeCapability)
class CommitteeCapabilityAdmin(admin.ModelAdmin):
    list_display = ("committee", "capability", "added_at")
    list_filter = ("capability",)
    search_fields = ("committee__name",)

    def has_module_permission(self, request):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or is_presidential_office_leader(request.user)

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)
