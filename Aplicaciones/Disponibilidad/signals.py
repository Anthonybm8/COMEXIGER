from django.db.models.signals import post_save
from django.dispatch import receiver
from Aplicaciones.Rendimiento.models import Rendimiento
from .models import Disponibilidad
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@receiver(post_save, sender=Rendimiento)
def actualizar_disponibilidad(sender, instance, created, **kwargs):
    if not created:
        return  

    numero_mesa = instance.numero_mesa  
    variedad = instance.variedad
    medida = instance.medida

    disponibilidad, creada = Disponibilidad.objects.get_or_create(
        numero_mesa=numero_mesa,
        variedad=variedad,
        medida=medida,
        defaults={
            'stock': 1,
            'fecha_entrada': instance.fecha_entrada
        }
    )

    if not creada:
        disponibilidad.stock += 1
        disponibilidad.save()

    # ---- WEBSOCKET COMPATIBLE ----
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        "disponibilidad_group",
        {
            "type": "stock_update",
            "data": {
                "id": disponibilidad.id,
                "numero_mesa": disponibilidad.numero_mesa,
                "variedad": disponibilidad.variedad,
                "medida": disponibilidad.medida,
                "stock": disponibilidad.stock,
                "fecha_entrada": str(disponibilidad.fecha_entrada),
                "fecha_salida": str(disponibilidad.fecha_salida) if disponibilidad.fecha_salida else ""
            }
        }
    )
