from channels.generic.websocket import AsyncWebsocketConsumer
import json

class RendimientoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("rendimientos", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("rendimientos", self.channel_name)

    # ✅ Evento principal: "type": "nuevo_rendimiento"
    async def nuevo_rendimiento(self, event):
        await self.send(text_data=json.dumps({
            "type": "nuevo_rendimiento",
            "data": event.get("data", {})
        }))

    # ✅ Si por alguna razón todavía usas "send_rendimiento"
    async def send_rendimiento(self, event):
        await self.send(text_data=json.dumps({
            "type": "send_rendimiento",
            "data": event.get("data", {})
        }))
