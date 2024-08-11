from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_real_time_notification(notification):
    channel_layer = get_channel_layer()
    group_name = f"user_{notification.user.id}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_notification',
            'message': notification.message,
        }
    )
