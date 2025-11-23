from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Rendimiento
from .serializers import RendimientoSerializer

channel_layer = get_channel_layer()

def notificar_rendimiento(rendimiento):
    data = RendimientoSerializer(rendimiento).data
    async_to_sync(channel_layer.group_send)(
        "rendimientos",
        {
            "type": "rendimiento_event",
            "data": data
        }
    )
