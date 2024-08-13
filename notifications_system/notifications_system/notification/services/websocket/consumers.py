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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None
        self.group_name = None

    async def connect(self):
        # Verificar si el usuario está autenticado
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if token is None:
            await self.close()
            return

        try:
            decoded_token = UntypedToken(token)
            self.user_id = decoded_token['user_id']
            # Si el token es válido, continúa con la conexión
            user = await database_sync_to_async(User.objects.get)(id=self.user_id)
            self.scope['user'] = user
            self.group_name = f'notifications_{self.user_id}'

            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()

        except (InvalidToken, TokenError):
            # Si el token es inválido, cierra la conexión
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )


class NotificationConsumer(NotificationConsumerBase):

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message_type = data.get('type')

        # {"type": "notifications_list", "page": 1, "page_size": 5}
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
            # Llama al servicio para marcar la notificación como leída
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
            # Llama al servicio para marcar la notificación como leída
            await sync_to_async(mark_notification_as_deleted)(notification_id)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'notification_delete',
                    'id': notification_id
                }
            )

    async def notification_message(self, event):
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
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'read',
            'data': data
        }))

    async def notification_read(self, event):
        notification_id = event['id']
        await self.send(text_data=json.dumps({
            'type': 'read',
            'id': notification_id
        }))

    async def notification_delete(self, event):
        notification_id = event['id']
        await self.send(text_data=json.dumps({
            'type': 'delete',
            'id': notification_id
        }))
