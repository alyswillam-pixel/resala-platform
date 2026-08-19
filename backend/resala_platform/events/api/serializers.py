from rest_framework import serializers
from resala_platform.events.models import Event, EventStateTransition, Budget

class EventStateTransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventStateTransition
        fields = ["id", "event", "from_state", "to_state", "action", "actor", "note", "created_at"]
        read_only_fields = ["id", "event", "from_state", "to_state", "action", "actor", "created_at"]

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ["id", "event", "amount", "status", "approved_by", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "approved_by", "created_at", "updated_at"]

class EventSerializer(serializers.ModelSerializer):
    budget = BudgetSerializer(read_only=True)
    
    class Meta:
        model = Event
        fields = ["id", "title", "description", "requester", "current_state", "budget", "created_at", "updated_at"]
        read_only_fields = ["id", "current_state", "requester", "created_at", "updated_at"]