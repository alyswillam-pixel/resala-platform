from django.contrib import admin

from .models import Budget
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "requester", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "requester__email")


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("event", "amount", "status", "approved_by", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("event__title", "approved_by__email")
