from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Disponibilidad
from .serializers import DisponibilidadSerializer


channel_layer = get_channel_layer()


def notificar_disponibilidad(disponibilidad):
    """
    Envía la disponibilidad por WebSocket
    """
    data = DisponibilidadSerializer(disponibilidad).data

    async_to_sync(channel_layer.group_send)(
        "disponibilidad",
        {
            "type": "nueva_disponibilidad",
            "data": data
        }
    )

