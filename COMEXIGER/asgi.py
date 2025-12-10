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

django_asgi_app = get_asgi_application()
# Importar routings de ambas apps
import Aplicaciones.Rendimiento.routing
import Aplicaciones.Disponibilidad.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter(
            Aplicaciones.Rendimiento.routing.websocket_urlpatterns
            +
            Aplicaciones.Disponibilidad.routing.websocket_urlpatterns
        )
    ),
})


