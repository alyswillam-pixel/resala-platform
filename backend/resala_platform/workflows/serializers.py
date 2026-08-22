from rest_framework import serializers

from .models import Workflow
from .models import WorkflowState
from .models import WorkflowTransition
from .models import WorkflowTransitionAction
from .models import WorkflowTransitionRule


class WorkflowStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowState
        fields = [
            "id",
            "workflow",
            "name",
            "description",
            "is_initial",
            "is_terminal",
            "review_committee",
        ]
        read_only_fields = ["id"]


class WorkflowTransitionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowTransitionRule
        fields = [
            "id",
            "transition",
            "authorization_type",
            "capability",
            "committee",
        ]
        read_only_fields = ["id"]


class WorkflowTransitionsActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowTransitionAction
        fields = [
            "id",
            "transition",
            "action_type",
            "value",
            "order",
        ]
        read_only_fields = ["id"]


class WorkflowTransitionSerializer(serializers.ModelSerializer):
    rules = WorkflowTransitionRuleSerializer(many=True, read_only=True)
    actions = WorkflowTransitionsActionSerializer(many=True, read_only=True)

    class Meta:
        model = WorkflowTransition
        fields = [
            "id",
            "workflow",
            "name",
            "description",
            "source",
            "target",
            "rules",
            "actions",
        ]
        read_only_fields = ["id"]


class WorkflowSerializer(serializers.ModelSerializer):
    states = WorkflowStateSerializer(many=True, read_only=True)
    transitions = WorkflowTransitionSerializer(many=True, read_only=True)

    class Meta:
        model = Workflow
        fields = [
            "id",
            "name",
            "description",
            "content_type",
            "is_active",
            "created_by",
            "created_at",
            "updated_at",
            "states",
            "transitions",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
        ]
