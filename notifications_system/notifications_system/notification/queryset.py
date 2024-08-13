from math import ceil

from django.db.models import F

from notification.models import UserNotification
from notification.serializers import UserNotificationSerializer


def mark_notification_as_read(notification_id):
    try:
        notification = UserNotification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
    except UserNotification.DoesNotExist:
        pass


def mark_notification_as_deleted(notification_id):
    try:
        notification = UserNotification.objects.get(id=notification_id)
        notification.is_deleted = True
        notification.save()
    except UserNotification.DoesNotExist:
        pass


def get_paginated_notifications(user_id, page, page_size=10):
    queryset = UserNotification.objects.filter(user_id=user_id).select_related(
        'notification'
    ).values(
        'id',
        'is_read',
        timestamp=F('notification__timestamp'),
        message=F('notification__message')
    )

    # Convirtiendo a lista de diccionarios
    notification_list = list(queryset)

    total_pages = ceil(len(notification_list) / page_size)

    # Asegurarse de que el número de página esté dentro de los límites
    page = max(1, min(page, total_pages))

    # Obtener el conjunto de datos paginado manualmente
    start = (page - 1) * page_size
    end = start + page_size
    result_page = queryset[start:end]

    serializer = UserNotificationSerializer(result_page, many=True)

    return serializer.data, total_pages
