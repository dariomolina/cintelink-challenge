from rest_framework import serializers
from notification.models import Notification, Tag, NotificationSubscription


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for the Tag model.

    This serializer converts Tag instances to and from JSON format.

    Fields:
        id (int): The unique identifier of the tag.
        name (str): The name of the tag.
    """

    class Meta:
        model = Tag
        fields = ['id', 'name']


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.

    This serializer converts Notification instances to and from JSON format.

    Fields:
        id (int): The unique identifier of the notification.
        tag (Tag): The tag associated with the notification.
        message (str): The content of the notification.
        timestamp (datetime): The time when the notification was created.
    """

    class Meta:
        model = Notification
        fields = ['id', 'tag', 'message', 'timestamp']


class NotificationSubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the NotificationSubscription model.

    This serializer converts NotificationSubscription instances to and from JSON format.

    Fields:
        id (int): The unique identifier of the subscription.
        user (User): The user subscribed to the notification.
        tag (Tag): The tag that the user is subscribed to.
        created_at (datetime): The time when the subscription was created.
    """

    class Meta:
        model = NotificationSubscription
        fields = ['id', 'user', 'tag', 'created_at']


class UserNotificationSerializer(serializers.Serializer):
    """
    Serializer for user notifications, used for sending notification data to clients.

    This serializer converts user notification data to and from JSON format.

    Fields:
        id (int): The unique identifier of the user notification.
        timestamp (datetime): The time when the notification was created.
        is_read (bool): Whether the notification has been read by the user.
        message (str): The content of the notification.
    """

    id = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    is_read = serializers.BooleanField()
    message = serializers.CharField()
