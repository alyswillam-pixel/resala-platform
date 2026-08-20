from django.contrib import admin

from resala_platform.committees.permissions import is_presidential_office_leader

from .models import TreasuryCommittee


@admin.register(TreasuryCommittee)
class TreasuryCommitteeAdmin(admin.ModelAdmin):
    list_display = ("committee", "added_at")
    autocomplete_fields = ("committee",)

    def _po_only(self, request, obj=None):
        return request.user.is_superuser or is_presidential_office_leader(request.user)

    has_module_permission = has_view_permission = _po_only
    has_add_permission = has_change_permission = has_delete_permission = _po_only
