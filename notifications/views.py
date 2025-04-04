"""
Notification views for retrieving user-specific notifications and marking them as read.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    """
    View to retrieve a list of notifications for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get a list of notifications for the current user,
        sorted by most recent first.
        """
        notifications = Notification.objects.filter(recipient=request.user).order_by(
            "-created_at"
        )
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class MarkNotificationReadView(APIView):
    """
    View to mark a specific notification as read for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        """
        Mark a notification as read.
        Only the recipient of the notification can perform this action.
        """
        try:
            notification = Notification.objects.get(
                id=notification_id, recipient=request.user
            )
            notification.read = True
            notification.save()
            return Response({"status": "notification marked as read"})
        except Notification.DoesNotExist:
            return Response(
                {"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND
            )
