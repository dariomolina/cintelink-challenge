from django.contrib.auth.models import User
from django.db import models
from auditlog.registry import auditlog


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Notification(models.Model):
    tag = models.ForeignKey('notification.Tag', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tag} - {self.timestamp}"


class NotificationSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    tag = models.ForeignKey('notification.Tag', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tag')

    def __str__(self):
        return f"{self.user.username} - {self.tag.name} - {self.created_at}"


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification = models.ForeignKey('notification.Notification', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'notification')

    def __str__(self):
        return f"{self.user.username} - {self.notification.tag.name} - {self.is_read}"


auditlog.register(Tag)
auditlog.register(Notification)
auditlog.register(NotificationSubscription)
auditlog.register(UserNotification)
