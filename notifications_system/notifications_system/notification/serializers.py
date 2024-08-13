from rest_framework import serializers
from notification.models import Notification, Tag, NotificationSubscription, UserNotification
from notification.services.websocket.notifications import send_real_time_notification


# class NotificationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Notification
#         fields = '__all__'
#
#     def create(self, validated_data):
#         instance = super().create(validated_data=validated_data)
#         send_real_time_notification(notification=instance)
#         return instance


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
