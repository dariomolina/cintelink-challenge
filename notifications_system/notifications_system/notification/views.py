from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from notification.models import Notification
from notification.serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, is_deleted=False)
