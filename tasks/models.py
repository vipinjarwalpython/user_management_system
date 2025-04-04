from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class Task(models.Model):
    """
    Model representing a task assigned to a user.

    Fields:
        title (str): Title of the task.
        description (str): Detailed information about the task.
        assigned_by (User): The user who assigned the task (Admin or Manager).
        assigned_to (User): The user to whom the task is assigned.
        deadline (datetime): Deadline by which the task must be completed.
        status (str): Current status of the task (Pending, In Progress, Completed, or Failed).
        created_at (datetime): Timestamp when the task was created.
        updated_at (datetime): Timestamp when the task was last updated.
    """
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_tasks",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks"
    )
    deadline = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


@receiver(post_save, sender=Task)
def handle_task_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs after a Task is saved.

    Calls a utility function to check and handle task status changes,
    such as sending notifications or triggering automatic logic.
    """
    from notifications.utils import check_task_status

    check_task_status(instance)
