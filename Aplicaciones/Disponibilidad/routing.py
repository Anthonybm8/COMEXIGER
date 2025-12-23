from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/disponibilidad/",consumers.DisponibilidadConsumer.as_asgi()),
]
