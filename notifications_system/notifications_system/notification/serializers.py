from rest_framework import serializers
from notification.models import Notification, Tag, NotificationSubscription


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ['id', 'tag', 'message', 'timestamp']


class NotificationSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = NotificationSubscription
        fields = ['id', 'user', 'tag', 'created_at']


class UserNotificationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    is_read = serializers.BooleanField()
    message = serializers.CharField()
