
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DisponibilidadConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("1")
        self.group_name = "disponibilidad_group"
        print("2")
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        print("3")
        await self.accept()
        print("4")

    async def disconnect(self, close_code):
        print("5")
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print("6")

    
    async def stock_update(self, event):
        print("7")
        data = event.get("data", {})
        print("8")
        
        await self.send(text_data=json.dumps(data))
        print("9")

    async def receive(self, text_data):
        print("10")
        try:
            print("11")
            payload = json.loads(text_data)
        except Exception:
            return
        print("12")
        await self.channel_layer.group_send(
            self.group_name,
            
            {
                "type": "stock.update",
                "data": payload
            }
            
        )
        print("13")
