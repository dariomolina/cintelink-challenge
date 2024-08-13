from django.contrib.auth.models import User
from django.db import models
from auditlog.registry import auditlog


class Tag(models.Model):
    """
    Represents a tag that can be associated with notifications.

    Attributes:
        name (str): The name of the tag, which must be unique.
    """

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Notification(models.Model):
    """
    Represents a notification that is associated with a specific tag.

    Attributes:
        tag (Tag): The tag associated with this notification.
        message (str): The content of the notification.
        timestamp (datetime): The time when the notification was created.
    """

    tag = models.ForeignKey('notification.Tag', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tag} - {self.timestamp}"


class NotificationSubscription(models.Model):
    """
    Represents a subscription where a user subscribes to notifications of a specific tag.

    Attributes:
        user (User): The user who is subscribed to the tag.
        tag (Tag): The tag to which the user is subscribed.
        created_at (datetime): The time when the subscription was created.

    Meta:
        unique_together: Ensures that a user can only subscribe to a specific tag once.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    tag = models.ForeignKey('notification.Tag', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tag')

    def __str__(self):
        return f"{self.user.username} - {self.tag.name} - {self.created_at}"


class UserNotification(models.Model):
    """
    Represents a notification sent to a user, tracking whether it has been read or deleted.

    Attributes:
        user (User): The user who received the notification.
        notification (Notification): The notification received by the user.
        is_read (bool): Whether the notification has been read by the user.
        is_deleted (bool): Whether the notification has been deleted by the user.

    Meta:
        unique_together: Ensures that a user cannot receive the same notification more than once.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification = models.ForeignKey('notification.Notification', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'notification')

    def __str__(self):
        return f"{self.user.username} - {self.notification.tag.name} - {self.is_read}"


# Registering models with auditlog to track changes.
auditlog.register(Tag)
auditlog.register(Notification)
auditlog.register(NotificationSubscription)
auditlog.register(UserNotification)
