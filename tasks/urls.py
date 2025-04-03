from django.urls import path
from .views import (
    TaskListCreateView,
    TaskDetailView,
    CheckOverdueTasksView,
    MarkTaskFailedView,
)

urlpatterns = [
    path("", TaskListCreateView.as_view(), name="task-list-create"),
    path("<int:task_id>/", TaskDetailView.as_view(), name="task-detail"),
    path("overdue/", CheckOverdueTasksView.as_view(), name="check-overdue-tasks"),
    path("<int:task_id>/fail/", MarkTaskFailedView.as_view(), name="mark-task-failed"),
]
