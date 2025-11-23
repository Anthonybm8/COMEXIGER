from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/rendimientos/", consumers.RendimientoConsumer.as_asgi()),
]
