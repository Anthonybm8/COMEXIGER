from channels.generic.websocket import AsyncWebsocketConsumer
import json
class RendimientoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("rendimientos", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("rendimientos", self.channel_name)

    async def nuevo_rendimiento(self, event):  # debe coincidir con 'type' en group_send
        await self.send(text_data=json.dumps(event["data"]))
