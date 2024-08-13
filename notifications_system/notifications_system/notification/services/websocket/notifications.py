from datetime import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_real_time_notification(user_notification):
    """
    Sends a real-time notification to a specific user's WebSocket group.

    This function triggers a message to be sent to the WebSocket group associated
    with a user, which is then handled by the WebSocket consumer on the client-side.

    Args:
        user_notification (UserNotification): The UserNotification instance
                                              containing the notification details.

    The message will be sent to the WebSocket consumer's `notification_message`
    handler method, which should be defined in the consumer.

    The message contains the following fields:
    - 'type': Specifies the handler method in the WebSocket consumer to be called.
    - 'id': The ID of the user notification.
    - 'message': The content of the notification.
    - 'is_read': A boolean indicating whether the notification has been read.
    - 'timestamp': The timestamp of the notification in ISO 8601 format.
    """
    channel_layer = get_channel_layer()
    group_name = f"notifications_{user_notification.user.id}"

    # Type specifies the name of the function in the WebSocket consumer that should handle this message
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
