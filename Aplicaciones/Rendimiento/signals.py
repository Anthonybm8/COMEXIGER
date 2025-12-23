from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Rendimiento
from .serializers import RendimientoSerializer
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Rendimiento


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()

def notificar_rendimiento(rendimiento):
    data = RendimientoSerializer(rendimiento).data
    async_to_sync(channel_layer.group_send)(
        "rendimientos",
        {
            "type": "nuevo_rendimiento",
            "data": data
        }
    )



