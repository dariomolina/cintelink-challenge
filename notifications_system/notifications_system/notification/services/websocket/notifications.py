from datetime import timezone

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_real_time_notification(user_notification):
    channel_layer = get_channel_layer()
    group_name = f"notifications_{user_notification.user.id}"

    # type is the name of the sending function in the NotificationConsumer
    # in this case is notification_message
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'notification_message',
            'id': user_notification.id,
            'message': user_notification.notification.message,
            'is_read': user_notification.is_read,
            'timestamp': user_notification.notification.timestamp.astimezone(timezone.utc).isoformat()
        }
    )
