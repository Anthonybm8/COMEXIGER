from django.urls import path
from .consumers import DisponibilidadConsumer

websocket_urlpatterns = [
    path("ws/disponibilidad/", DisponibilidadConsumer.as_asgi()),
]
