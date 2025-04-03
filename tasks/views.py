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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == "ADMIN":
            # Admin can see all tasks
            tasks = Task.objects.all()
        elif request.user.role == "MANAGER":
            # Manager can see tasks they assigned
            tasks = Task.objects.filter(assigned_by=request.user)
        else:
            # Regular users can see only their tasks
            tasks = Task.objects.filter(assigned_to=request.user)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Only Admin and Manager can create tasks
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
    permission_classes = [IsAuthenticated]

    def get_object(self, task_id):
        try:
            task = Task.objects.get(id=task_id)
            # Check permissions based on role
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
        task = self.get_object(task_id)
        if not task:
            return Response(
                {"error": "Task not found or not authorized"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, task_id):
        task = self.get_object(task_id)
        if not task:
            return Response(
                {"error": "Task not found or not authorized"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only Admin and Manager who assigned the task can update all fields
        if request.user.role in ["ADMIN", "MANAGER"] and (
            request.user.role == "ADMIN" or task.assigned_by == request.user
        ):
            serializer = TaskSerializer(
                task, data=request.data, context={"request": request}, partial=True
            )
        else:
            # Regular users can only update status
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
        task = self.get_object(task_id)
        if not task:
            return Response(
                {"error": "Task not found or not authorized"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only Admin and Manager who assigned the task can delete it
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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Only Admin and Managers can check overdue tasks
        if request.user.role not in ["ADMIN", "MANAGER"]:
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN
            )

        now = timezone.now()

        if request.user.role == "ADMIN":
            # Admin can see all overdue tasks
            overdue_tasks = Task.objects.filter(
                deadline__lt=now, status__in=["PENDING", "IN_PROGRESS"]
            )
        else:
            # Manager can see overdue tasks they assigned
            overdue_tasks = Task.objects.filter(
                deadline__lt=now,
                status__in=["PENDING", "IN_PROGRESS"],
                assigned_by=request.user,
            )

        serializer = TaskSerializer(overdue_tasks, many=True)
        return Response(serializer.data)


class MarkTaskFailedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        # Only Admin and Managers can mark tasks as failed
        if request.user.role not in ["ADMIN", "MANAGER"]:
            return Response(
                {"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            task = Task.objects.get(id=task_id)

            # Manager can only modify tasks they assigned
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

            # Mark task as failed
            task.status = "FAILED"
            task.save()

            # Increment failed tasks count for the user
            user = task.assigned_to
            user.failed_tasks += 1

            # Auto-deactivate user if they have 5 or more failed tasks
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
