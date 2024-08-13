from django.contrib import admin
from notification.models import (
    Notification, UserNotification, NotificationSubscription, Tag
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Notification objects.

    This class provides the admin interface for viewing, adding, and managing
    notifications within the Django admin panel.
    """
    pass


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for managing UserNotification objects.

    This class provides the admin interface for viewing, adding, and managing
    user notifications within the Django admin panel.
    """
    pass


@admin.register(NotificationSubscription)
class NotificationSubscriptionAdmin(admin.ModelAdmin):
    """
    Admin interface for managing NotificationSubscription objects.

    This class provides the admin interface for viewing, adding, and managing
    notification subscriptions within the Django admin panel.
    """
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Tag objects.

    This class provides the admin interface for viewing, adding, and managing
    tags within the Django admin panel.
    """
    pass
