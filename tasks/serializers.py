from rest_framework import serializers
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    assigned_by_email = serializers.EmailField(
        source="assigned_by.email", read_only=True
    )
    assigned_to_email = serializers.EmailField(
        source="assigned_to.email", read_only=True
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "assigned_by",
            "assigned_to",
            "assigned_by_email",
            "assigned_to_email",
            "deadline",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["assigned_by", "created_at", "updated_at"]

    def validate_assigned_to(self, value):
        if not value.is_active:
            raise serializers.ValidationError("Cannot assign task to inactive user.")
        if value.role != "USER":
            raise serializers.ValidationError(
                "Tasks can only be assigned to regular users."
            )
        return value

    def create(self, validated_data):
        validated_data["assigned_by"] = self.context["request"].user
        return super().create(validated_data)


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "status", "updated_at"]
        read_only_fields = ["id", "updated_at"]
