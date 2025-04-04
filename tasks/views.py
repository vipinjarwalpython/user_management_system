"""
Task management views with role-based access control for listing, creating, 
updating, deleting, and managing task statuses like overdue and failed.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import Task
from .serializers import TaskSerializer, TaskStatusUpdateSerializer
from users.models import User


class TaskListCreateView(APIView):
    """
    View to list all tasks based on user role and create new tasks.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve tasks based on the user's role:
        - Admin: all tasks
        - Manager: tasks assigned by them
        - User: tasks assigned to them
        """
        if request.user.role == "ADMIN":
            tasks = Task.objects.all()
        elif request.user.role == "MANAGER":
            tasks = Task.objects.filter(assigned_by=request.user)
        else:
            tasks = Task.objects.filter(assigned_to=request.user)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new task.
        Only Admin and Manager roles are allowed to assign tasks.
        """
        if request.user.role not in ["ADMIN", "MANAGER"]:
            return Response(
                {"error": "Only Admin and Manager can assign tasks"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    """
    View to retrieve, update, or delete a specific task based on the user's role.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, task_id):
        """
        Retrieve a task by ID with permission checks based on user role.
        """
        try:
            task = Task.objects.get(id=task_id)
            if self.request.user.role == "ADMIN":
                return task
            elif (
                self.request.user.role == "MANAGER"
                and task.assigned_by == self.request.user
            ):
                return task
            elif (
                self.request.user.role == "USER"
                and task.assigned_to == self.request.user
            ):
                return task
            return None
        except Task.DoesNotExist:
            return None

    def get(self, request, task_id):
        """
        Retrieve task details if user has permission.
        """
        task = self.get_object(task_id)
        if not task:
            return Response(
                {"error": "Task not found or not authorized"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, task_id):
        """
        Update task details:
        - Admin or Manager who created the task can update all fields.
        - Users can only update the task status.
        """
        task = self.get_object(task_id)
        if not task:
            return Response(
                {"error": "Task not found or not authorized"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role in ["ADMIN", "MANAGER"] and (
            request.user.role == "ADMIN" or task.assigned_by == request.user
        ):
            serializer = TaskSerializer(
                task, data=request.data, context={"request": request}, partial=True
            )
        else:
            if "status" not in request.data or len(request.data) > 1:
                return Response(
                    {"error": "You can only update task status"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = TaskStatusUpdateSerializer(
                task, data=request.data, partial=True
            )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id):
        """
        Delete a task:
        - Admin or Manager who assigned the task can delete it.
        """
        task = self.get_object(task_id)
        if not task:
            return Response(
                {"error": "Task not found or not authorized"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role == "ADMIN" or (
            request.user.role == "MANAGER" and task.assigned_by == request.user
        ):
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"error": "Not authorized to delete this task"},
            status=status.HTTP_403_FORBIDDEN,
        )


class CheckOverdueTasksView(APIView):
    """
    View to check overdue tasks based on deadline and current time.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve tasks that are overdue:
        - Admin: all overdue tasks
        - Manager: tasks they assigned that are overdue
        """
        if request.user.role not in ["ADMIN", "MANAGER"]:
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN
            )

        now = timezone.now()

        if request.user.role == "ADMIN":
            overdue_tasks = Task.objects.filter(
                deadline__lt=now, status__in=["PENDING", "IN_PROGRESS"]
            )
        else:
            overdue_tasks = Task.objects.filter(
                deadline__lt=now,
                status__in=["PENDING", "IN_PROGRESS"],
                assigned_by=request.user,
            )

        serializer = TaskSerializer(overdue_tasks, many=True)
        return Response(serializer.data)


class MarkTaskFailedView(APIView):
    """
    View to manually mark a task as failed and auto-deactivate user if needed.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        """
        Mark a task as failed:
        - Only Admin or Manager who assigned it can perform the action.
        - Increments user's failed task count.
        - Auto-deactivates the user after 5 failed tasks and sends a notification.
        """
        if request.user.role not in ["ADMIN", "MANAGER"]:
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            task = Task.objects.get(id=task_id)

            if request.user.role == "MANAGER" and task.assigned_by != request.user:
                return Response(
                    {"error": "You can only modify tasks you assigned"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if task.status == "FAILED":
                return Response(
                    {"error": "Task is already marked as failed"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            task.status = "FAILED"
            task.save()

            user = task.assigned_to
            user.failed_tasks += 1

            if user.failed_tasks >= 5:
                user.is_active = False
                from notifications.utils import send_deactivation_notification
                send_deactivation_notification(user, task.assigned_by)

            user.save()

            return Response(
                {
                    "message": "Task marked as failed",
                    "user_failed_tasks": user.failed_tasks,
                }
            )

        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )
