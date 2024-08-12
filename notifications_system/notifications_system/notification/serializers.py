from rest_framework import serializers
from notification.models import Notification
from notification.notifications import send_real_time_notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

    def create(self, validated_data):
        instance = super().create(validated_data=validated_data)
        send_real_time_notification(notification=instance)
        return instance
