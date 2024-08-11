from django.contrib.auth.models import User
from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    tag = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.message


class UserTagSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tag')

    def __str__(self):
        return f"{self.user.username} - {self.tag}"
