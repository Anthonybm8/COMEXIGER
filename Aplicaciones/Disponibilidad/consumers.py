from channels.generic.websocket import AsyncWebsocketConsumer
import json

class DisponibilidadConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add(
            "disponibilidad",   # nombre del grupo
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "disponibilidad",
            self.channel_name
        )

    # Evento cuando se crea o actualiza disponibilidad
    async def nueva_disponibilidad(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    # Evento genérico para enviar disponibilidad
    async def send_disponibilidad(self, event):
        await self.send(text_data=json.dumps(event["data"]))
