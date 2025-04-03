from django.db import models
from django.conf import settings


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ("TASK_OVERDUE", "Task Overdue"),
        ("USER_DEACTIVATED", "User Deactivated"),
        ("TASK_COMPLETED", "Task Completed"),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    read = models.BooleanField(default=False)
    related_task_id = models.IntegerField(null=True, blank=True)
    related_user_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} to {self.recipient}"
