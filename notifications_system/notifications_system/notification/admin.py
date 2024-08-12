from django.contrib import admin

from notification.models import Notification


@admin.register(Notification)
class ModelNotification(admin.ModelAdmin):
    pass
