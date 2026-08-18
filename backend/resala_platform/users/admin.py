from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from resala_platform.committees.models import CommitteeRole
from resala_platform.committees.permissions import get_led_committee
from resala_platform.committees.permissions import is_presidential_office_leader

from .forms import UserAdminChangeForm, UserAdminCreationForm
from .models import User
from .tasks import send_new_user_credentials_email

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("auc_email", "password")}),
        (_("Personal info"), {"fields": ("name", "auc_id")}),
        (_("Committee"), {"fields": ("committee_role",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["auc_email", "name", "committee_role", "is_staff", "is_superuser"]
    search_fields = ["name", "auc_email", "auc_id"]
    ordering = ["auc_email"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "auc_email",
                    "auc_id",
                    "committee_role",
                ),
            },
        ),
    )

    # --- Committee-scoped access control -----------------------------------
    #
    # Presidential Office leadership sees and manages everyone.
    # A Director/Vice-Director of another committee only sees and manages
    # users whose committee_role belongs to that committee.
    # is_staff/is_superuser/groups/user_permissions are never hand-edited by
    # anyone but a true superuser — is_staff is signal-driven off
    # Committee.director/vice_director, so this also closes the
    # self-elevation path for Presidential Office and Directors alike.

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or is_presidential_office_leader(request.user):
            return qs
        led = get_led_committee(request.user)
        return qs.filter(committee_role__committee=led) if led else qs.none()

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        if obj is not None:
            return obj
        # Fall back to unfiltered queryset so that existing-but-forbidden
        # objects get a proper 403 instead of a misleading 302 redirect.
        model = self.model
        try:
            pk = model._meta.pk.get_prep_value(object_id)
            return model._default_manager.get(pk=pk)
        except (model.DoesNotExist, ValueError):
            return None

    def has_module_permission(self, request, obj=None):
        return (
            request.user.is_superuser
            or is_presidential_office_leader(request.user)
            or get_led_committee(request.user) is not None
        )

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser or is_presidential_office_leader(request.user):
            return True
        led = get_led_committee(request.user)
        if not led:
            return False
        if obj is None:
            return True
        return bool(obj.committee_role_id and obj.committee_role.committee_id == led.id)

    has_add_permission = has_module_permission

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or is_presidential_office_leader(request.user):
            return True
        led = get_led_committee(request.user)
        if not led:
            return False
        if obj is None:
            return True
        return bool(obj.committee_role_id and obj.committee_role.committee_id == led.id)

    has_delete_permission = has_change_permission

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if request.user.is_superuser:
            return fieldsets
        locked = ("is_staff", "is_superuser", "groups", "user_permission")
        filtered = []
        for name, opts in fieldsets:
            fields = tuple(f for f in opts["fields"] if f not in locked)
            if fields:
                filtered.append((name, {**opts, "fields": fields}))

        return filtered

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Directors/vice-directors must assign a committee role when creating
        # a user, otherwise the user disappears from their scoped queryset.
        # Editing allows clearing the role (e.g. to remove someone).
        if obj is None and not (
            request.user.is_superuser or is_presidential_office_leader(request.user)
        ):
            if "committee_role" in form.base_fields:
                form.base_fields["committee_role"].required = True
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "committee_role" and not (
            request.user.is_superuser or is_presidential_office_leader(request.user)
        ):
            led = get_led_committee(request.user)
            kwargs["queryset"] = (
                CommitteeRole.objects.filter(committee=led)
                if led
                else CommitteeRole.objects.none()
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        is_new = not change

        if not (
            request.user.is_superuser or is_presidential_office_leader(request.user)
        ):
            led = get_led_committee(request.user)
            role = obj.committee_role
            if not led or (role and role.committee_id != led.id):
                raise PermissionDenied(
                    "You may only manage users within your own committee",
                )

        if is_new:
            obj.set_unusable_password()

        super().save_model(request, obj, form, change)

        # Fire celery to send email after transaction commits.
        # ATOMIC_REQUESTS wraps the request in a transaction, so the user
        # row isn't visible to the worker until the transaction commits.
        if is_new:
            base_url = request.build_absolute_uri('/')[:-1]
            transaction.on_commit(
                lambda: send_new_user_credentials_email.delay(obj.pk, base_url)
            )
