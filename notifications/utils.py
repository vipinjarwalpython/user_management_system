from django.utils import timezone
from .models import Notification


def check_task_status(task):
    """
    Check if task is overdue and create notification if needed.
    This is called by the signal handler when a task is saved.
    """
    # Check if task is overdue
    if task.deadline < timezone.now() and task.status in ["PENDING", "IN_PROGRESS"]:
        create_overdue_notification(task)

    # Check if task status changed to completed
    if task.status == "COMPLETED":
        create_completion_notification(task)

    # Check if task status changed to failed
    if task.status == "FAILED":
        increment_failed_tasks(task.assigned_to)


def create_overdue_notification(task):
    """Create notification for manager when task is overdue"""
    message = f"Task '{task.title}' assigned to {task.assigned_to.email} is overdue."

    # Create notification for the manager who assigned the task
    Notification.objects.create(
        recipient=task.assigned_by,
        notification_type="TASK_OVERDUE",
        message=message,
        related_task_id=task.id,
        related_user_id=task.assigned_to.id,
    )

    # In a real application, this could also send an email
    print(f"NOTIFICATION: {message}")


def create_completion_notification(task):
    """Create notification when task is completed"""
    message = f"Task '{task.title}' has been completed by {task.assigned_to.email}."

    # Create notification for the manager who assigned the task
    Notification.objects.create(
        recipient=task.assigned_by,
        notification_type="TASK_COMPLETED",
        message=message,
        related_task_id=task.id,
        related_user_id=task.assigned_to.id,
    )

    # In a real application, this could also send an email
    print(f"NOTIFICATION: {message}")


def send_deactivation_notification(user, manager):
    """Send notification when user is deactivated for failing too many tasks"""
    message = f"User {user.email} has been automatically deactivated due to failing 5 or more tasks."

    # Create notification for the manager
    Notification.objects.create(
        recipient=manager,
        notification_type="USER_DEACTIVATED",
        message=message,
        related_user_id=user.id,
    )

    # In a real application, this could also send an email
    print(f"NOTIFICATION: {message}")


def increment_failed_tasks(user):
    """Increment the failed_tasks counter for a user"""
    from django.contrib.auth import get_user_model

    User = get_user_model()

    user.failed_tasks += 1

    # Check if user should be deactivated
    if user.failed_tasks >= 5:
        user.is_active = False

    user.save()

    # In a real application, this could also send an email notification
    print(f"User {user.email} now has {user.failed_tasks} failed tasks.")
