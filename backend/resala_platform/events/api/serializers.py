from rest_framework import serializers
from resala_platform.events.models import (
    Event,
    EventStateTransition,
    Budget,
    Request,
    RequestStateTransition,
    RequestAssignmentHistory,
    RequestEscalation,
)

class EventStateTransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventStateTransition
        fields = "__all__"
        read_only_fields = ["created_at"]

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

class EventSerializer(serializers.ModelSerializer):
    budget = BudgetSerializer(read_only=True)
    
    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["current_state", "created_at", "updated_at"]

class RequestStateTransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestStateTransition
        fields = "__all__"
        read_only_fields = ["created_at"]

class RequestAssignmentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestAssignmentHistory
        fields = "__all__"
        read_only_fields = ["created_at"]

class RequestEscalationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestEscalation
        fields = "__all__"
        read_only_fields = ["status", "created_at", "resolved_at"]

class RequestSerializer(serializers.ModelSerializer):
    escalations = RequestEscalationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Request
        fields = "__all__"
        read_only_fields = ["current_state", "created_at", "updated_at"]