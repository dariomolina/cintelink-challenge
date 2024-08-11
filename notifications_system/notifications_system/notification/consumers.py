import json

from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = f'notifications_{self.scope["user"].id}'
        # Verificar si el usuario está autenticado
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if token is None:
            await self.close()
            return

        try:
            decoded_token = UntypedToken(token)
            user_id = decoded_token['user_id']
            # Si el token es válido, continúa con la conexión
            user = await database_sync_to_async(User.objects.get)(id=user_id)
            self.scope['user'] = user
            self.group_name = f'notifications_{self.scope["user"].id}'

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

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data['message']

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'notification_message',
                'message': message
            }
        )

    async def notification_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
