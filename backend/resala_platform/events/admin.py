from django.contrib import admin
from .models import Event, EventStateTransition, Budget

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "requester", "current_state", "created_at")
    list_filter = ("current_state", "created_at")
    search_fields = ("title", "requester__email")

@admin.register(EventStateTransition)
class EventStateTransitionAdmin(admin.ModelAdmin):
    list_display = ("event", "from_state", "to_state", "actor", "created_at")
    list_filter = ("from_state", "to_state", "created_at")
    search_fields = ("event__title", "actor__email")

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("event", "amount", "status", "approved_by", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("event__title", "approved_by__email")
