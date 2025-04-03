from django.core.management.base import BaseCommand
from django.utils import timezone
from tasks.models import Task
from notifications.utils import create_overdue_notification


class Command(BaseCommand):
    help = "Check for overdue tasks and send notifications"

    def handle(self, *args, **kwargs):
        now = timezone.now()

        # Find overdue tasks that are still pending or in progress
        overdue_tasks = Task.objects.filter(
            deadline__lt=now, status__in=["PENDING", "IN_PROGRESS"]
        )

        for task in overdue_tasks:
            create_overdue_notification(task)

        self.stdout.write(
            self.style.SUCCESS(f"Checked {overdue_tasks.count()} overdue tasks")
        )
