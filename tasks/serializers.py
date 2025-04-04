from rest_framework import serializers
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model used to create and retrieve task details.

    Fields:
        - assigned_by_email: Read-only email of the user who assigned the task.
        - assigned_to_email: Read-only email of the user to whom the task is assigned.

    Validations:
        - Ensures the assigned user is active and has the 'USER' role.
    """
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
        """
        Validate the 'assigned_to' field to ensure the user is active and is a regular user.

        Args:
            value (User): The user to whom the task is being assigned.

        Raises:
            ValidationError: If the user is inactive or not a regular 'USER'.

        Returns:
            User: The validated user.
        """
        if not value.is_active:
            raise serializers.ValidationError("Cannot assign task to inactive user.")
        if value.role != "USER":
            raise serializers.ValidationError(
                "Tasks can only be assigned to regular users."
            )
        return value

    def create(self, validated_data):
        """
        Override the create method to automatically set the assigned_by field
        to the currently authenticated user (Admin or Manager).

        Args:
            validated_data (dict): Validated task data.

        Returns:
            Task: The created Task instance.
        """
        validated_data["assigned_by"] = self.context["request"].user
        return super().create(validated_data)


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer used specifically for updating the status of a task.

    This is typically used by regular users to update their own task status.
    """
    class Meta:
        model = Task
        fields = ["id", "status", "updated_at"]
        read_only_fields = ["id", "updated_at"]
