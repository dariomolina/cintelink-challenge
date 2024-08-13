from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Tag, Notification, NotificationSubscription, UserNotification
from .serializers import (
    TagSerializer,
    NotificationSerializer,
    NotificationSubscriptionSerializer,
)
from .services.websocket.notifications import send_real_time_notification


class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Tag objects.

    Provides CRUD operations for Tag instances. Accessible only by admin users.

    Permissions:
        - IsAdminUser: Only admin users can access this view.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Notification objects.

    Provides CRUD operations for Notification instances. Accessible only by authenticated users.

    Permissions:
        - IsAuthenticated: Only authenticated users can access this view.
    """

    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def perform_create(self, serializer):
        """
        This method retrieves the tag associated with the notification, creates UserNotification
        instances for users subscribed to that tag, and sends real-time notifications to those users.

        Args:
            serializer (NotificationSerializer): The serializer instance used to save the notification.
        """
        tag_id = self.request.data.get('tag', None)
        tag = Tag.objects.get(id=tag_id)
        notification = serializer.save()

        user_ids = NotificationSubscription.objects.filter(
            tag=tag
        ).values_list(
            'user_id', flat=True
        )

        user_notifications = []
        for user_id in user_ids:
            user_notification = UserNotification.objects.create(
                user_id=user_id,
                notification=notification
            )
            user_notifications.append(user_notification)
            send_real_time_notification(user_notification=user_notification)


class NotificationSubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing NotificationSubscription objects.

    Provides CRUD operations for NotificationSubscription instances. Accessible only by authenticated users.

    Permissions:
        - IsAuthenticated: Only authenticated users can access this view.
    """

    queryset = NotificationSubscription.objects.all()
    serializer_class = NotificationSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        This  method save the user automatically when creating a NotificationSubscription.

        Args:
            serializer (NotificationSubscriptionSerializer): The serializer instance used to save the subscription.
        """
        serializer.save(user=self.request.user)
