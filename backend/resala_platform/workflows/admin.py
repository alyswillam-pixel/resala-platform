from django.contrib import admin

from .models import Workflow
from .models import WorkflowInstance
from .models import WorkflowState
from .models import WorkflowTransition
from .models import WorkflowTransitionAction
from .models import WorkflowTransitionLog
from .models import WorkflowTransitionRule


class WorkflowStateInline(admin.TabularInline):
    model = WorkflowState
    extra = 1


class WorkflowTransitionInline(admin.TabularInline):
    model = WorkflowTransition
    fk_name = "workflow"
    extra = 1


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "content_type",
        "is_active",
        "created_by",
        "created_at",
    )
    list_filter = ("content_type", "is_active")
    search_fields = ("name", "description")
    readonly_fields = ("created_by", "created_at", "updated_at")
    inlines = (WorkflowStateInline, WorkflowTransitionInline)

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user

        super().save_model(request, obj, form, change)


@admin.register(WorkflowState)
class WorkflowStateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "workflow",
        "is_initial",
        "is_terminal",
        "review_committee",
    )
    list_filter = ("workflow", "is_initial", "is_terminal")
    search_fields = ("name", "workflow__name")


class WorkflowTransitionRuleInline(admin.TabularInline):
    model = WorkflowTransitionRule
    extra = 1


class WorkflowTransitionActionInline(admin.TabularInline):
    model = WorkflowTransitionAction
    extra = 1


@admin.register(WorkflowTransition)
class WorkflowTransitionAdmin(admin.ModelAdmin):
    list_display = ("name", "workflow", "source", "target")
    list_filter = ("workflow",)
    search_fields = ("name", "workflow__name")
    inlines = [WorkflowTransitionRuleInline, WorkflowTransitionActionInline]


@admin.register(WorkflowTransitionRule)
class WorkflowTransitionRuleAdmin(admin.ModelAdmin):
    list_display = ("transition", "authorization_type", "capability", "committee")
    list_filter = ("authorization_type",)


@admin.register(WorkflowTransitionAction)
class WorkflowTransitionActionAdmin(admin.ModelAdmin):
    list_display = ("transition", "action_type", "value", "order")
    list_filter = ("action_type",)


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = (
        "workflow",
        "current_state",
        "content_type",
        "object_id",
        "created_at",
    )
    list_filter = ("workflow", "current_state", "content_type")
    readonly_fields = (
        "workflow",
        "current_state",
        "content_type",
        "object_id",
        "created_at",
        "updated_at",
    )


@admin.register(WorkflowTransitionLog)
class WorkflowTransitionLogAdmin(admin.ModelAdmin):
    list_display = (
        "instance",
        "transition",
        "from_state",
        "to_state",
        "actor",
        "created_at",
    )
    list_filter = ("transition__workflow", "created_at")
    readonly_fields = (
        "instance",
        "transition",
        "from_state",
        "to_state",
        "actor",
        "note",
        "created_at",
    )
