from rest_framework import serializers

from resala_platform.events.models import Budget
from resala_platform.events.models import Event


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = [
            "id",
            "event",
            "amount",
            "status",
            "approved_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "approved_by", "created_at", "updated_at"]


class EventSerializer(serializers.ModelSerializer):
    budget = BudgetSerializer(read_only=True)
    current_state = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "requester",
            "current_state",
            "budget",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "current_state",
            "requester",
            "created_at",
            "updated_at",
        ]

    def get_current_state(self, obj):
        from django.core.exceptions import ObjectDoesNotExist

        try:
            return obj.workflow_instance.get().current_state.name
        except ObjectDoesNotExist:
            return None
