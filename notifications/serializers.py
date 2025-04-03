from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
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
