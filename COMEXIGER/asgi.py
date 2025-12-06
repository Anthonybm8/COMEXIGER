"""
ASGI config for COMEXIGER project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'COMEXIGER.settings')

import Aplicaciones.Rendimiento.routing  # <--- exacto con mayúsculas

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            Aplicaciones.Rendimiento.routing.websocket_urlpatterns
        )
    ),
})

