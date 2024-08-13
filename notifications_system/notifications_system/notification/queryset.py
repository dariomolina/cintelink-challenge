from math import ceil
from django.db.models import F
from notification.models import UserNotification
from notification.serializers import UserNotificationSerializer


def mark_notification_as_read(notification_id):
    """
    Marks a specific notification as read by setting its `is_read` field to True.

    Args:
        notification_id (int): The ID of the notification to mark as read.

    If the notification does not exist, no action is taken.
    """
    try:
        notification = UserNotification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
    except UserNotification.DoesNotExist:
        pass


def mark_notification_as_deleted(notification_id):
    """
    Marks a specific notification as deleted by setting its `is_deleted` field to True.

    Args:
        notification_id (int): The ID of the notification to mark as deleted.

    If the notification does not exist, no action is taken.
    """
    try:
        notification = UserNotification.objects.get(id=notification_id)
        notification.is_deleted = True
        notification.save()
    except UserNotification.DoesNotExist:
        pass


def get_paginated_notifications(user_id, page, page_size=10):
    """
    Retrieves a paginated list of notifications for a specific user.

    Args:
        user_id (int): The ID of the user whose notifications are to be retrieved.
        page (int): The page number to retrieve.
        page_size (int, optional): The number of notifications per page. Defaults to 10.

    Returns:
        tuple: A tuple containing two elements:
            - A list of serialized notifications for the requested page.
            - The total number of pages available.

    The notifications are filtered for the specified user and paginated manually.
    """
    queryset = UserNotification.objects.filter(user_id=user_id).select_related(
        'notification'
    ).values(
        'id',
        'is_read',
        timestamp=F('notification__timestamp'),
        message=F('notification__message')
    )

    notification_list = list(queryset)

    total_pages = ceil(len(notification_list) / page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    result_page = notification_list[start:end]

    serializer = UserNotificationSerializer(result_page, many=True)

    return serializer.data, total_pages
