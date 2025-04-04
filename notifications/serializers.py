from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.

    This serializer is used to convert Notification instances to and from JSON format.
    It includes fields such as the notification type, message, read status, and related
    task/user information. All fields are read-only to ensure notifications cannot be 
    modified via the API.
    """
    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "message",
            "read",
            "related_task_id",
            "related_user_id",
            "created_at",
        ]
        read_only_fields = fields
