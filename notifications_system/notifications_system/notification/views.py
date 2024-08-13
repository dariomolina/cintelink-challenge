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
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def perform_create(self, serializer):
        tag_id = self.request.data.get('tag', None)
        # message = self.request.data.get('message', '')

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
    queryset = NotificationSubscription.objects.all()
    serializer_class = NotificationSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
