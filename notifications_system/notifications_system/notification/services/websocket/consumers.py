import json

from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken

from notification.queryset import (
    get_paginated_notifications,
    mark_notification_as_read,
    mark_notification_as_deleted
)


class NotificationConsumerBase(AsyncWebsocketConsumer):
    """
    Base WebSocket consumer for handling notification-related operations.

    Attributes:
        user_id (int|None): The ID of the authenticated user.
        group_name (str|None): The name of the WebSocket group associated with the user.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the NotificationConsumerBase with default attributes.
        """
        super().__init__(*args, **kwargs)
        self.user_id = None
        self.group_name = None

    async def connect(self):
        """
        Handle the WebSocket connection.

        Verifies the user's authentication via JWT token passed in the query string.
        If authenticated, adds the user to a group for receiving notifications.
        """
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if token is None:
            await self.close()
            return

        try:
            decoded_token = UntypedToken(token)
            self.user_id = decoded_token['user_id']
            # If the token is valid, continue with the connection
            user = await database_sync_to_async(User.objects.get)(id=self.user_id)
            self.scope['user'] = user
            self.group_name = f'notifications_{self.user_id}'

            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()

        except (InvalidToken, TokenError):
            # If the token is invalid, close the connection
            await self.close()

    async def disconnect(self, close_code):
        """
        Handle the WebSocket disconnection.

        Removes the user from the notification group.
        """
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )


class NotificationConsumer(NotificationConsumerBase):
    """
    WebSocket consumer that handles receiving and processing notification-related messages.
    Inherits from NotificationConsumerBase.

    Methods:
        receive: Handles incoming WebSocket messages and processes them based on the message type.
        notification_message: Sends a notification message to the client.
        notifications_list: Sends a list of notifications to the client.
        notification_read: Sends a message indicating a notification has been read.
        notification_delete: Sends a message indicating a notification has been deleted.
    """

    async def receive(self, text_data=None, bytes_data=None):
        """
        Handle incoming WebSocket messages.

        Processes different types of messages like retrieving notifications,
        marking notifications as read, and marking notifications as deleted.

        Args:
            text_data (str): The JSON-encoded message received from the client.
            bytes_data (bytes): Raw bytes received (not used here).
        """
        data = json.loads(text_data)
        message_type = data.get('type')

        # Handle different message types
        if message_type == 'notifications_list':
            page = data.get('page', 1)
            page_size = data.get('page_size', 10)
            notifications_data, total = await sync_to_async(
                get_paginated_notifications
            )(self.user_id, page, page_size)
            await self.send(text_data=json.dumps({
                'type': 'notifications_list',
                'data': notifications_data,
                'total_pages': total
            }))
        elif message_type == 'read':
            notification_id = data.get('id')
            # Call the service to mark the notification as read
            await sync_to_async(mark_notification_as_read)(notification_id)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'notification_read',
                    'id': notification_id
                }
            )
        elif message_type == 'deleted':
            notification_id = data.get('id')
            # Call the service to mark the notification as deleted
            await sync_to_async(mark_notification_as_deleted)(notification_id)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'notification_delete',
                    'id': notification_id
                }
            )

    async def notification_message(self, event):
        """
        Send a notification message to the client.

        Args:
            event (dict): Event data containing the notification details.
        """
        notification_id = event['id']
        message = event['message']
        timestamp = event['timestamp']
        is_read = event['is_read']
        await self.send(text_data=json.dumps({
            'id': notification_id,
            'message': message,
            'is_read': is_read,
            'timestamp': timestamp
        }))

    async def notifications_list(self, event):
        """
        Send a list of notifications to the client.

        Args:
            event (dict): Event data containing the list of notifications.
        """
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'read',
            'data': data
        }))

    async def notification_read(self, event):
        """
        Send a message indicating a notification has been read.

        Args:
            event (dict): Event data containing the notification ID.
        """
        notification_id = event['id']
        await self.send(text_data=json.dumps({
            'type': 'read',
            'id': notification_id
        }))

    async def notification_delete(self, event):
        """
        Send a message indicating a notification has been deleted.

        Args:
            event (dict): Event data containing the notification ID.
        """
        notification_id = event['id']
        await self.send(text_data=json.dumps({
            'type': 'delete',
            'id': notification_id
        }))
