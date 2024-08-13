from django.urls import path
from notification.services.websocket.consumers import NotificationConsumer

# Define the WebSocket URL patterns for the application.
# This is where the Django Channels will route WebSocket connections.

websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]
