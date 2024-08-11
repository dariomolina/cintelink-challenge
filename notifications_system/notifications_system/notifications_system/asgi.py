"""
ASGI config for chatbot project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""
import django
import os

# This line fixing this error
# "django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet."
django.setup(set_prefix=False)

# First, import django.core.asgi
from django.core.asgi import get_asgi_application as django_asgi_app
from channels.routing import ProtocolTypeRouter, URLRouter

from notification.routing import websocket_urlpatterns
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notifications_system.settings.local')

application = ProtocolTypeRouter({
    "http": django_asgi_app(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
