import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            # اطمینان از اینکه داده‌های دریافتی به درستی بارگذاری می‌شود
            if text_data:
                text_data_json = json.loads(text_data)
                message = text_data_json.get('message', '')

                # بررسی اینکه پیام خالی نباشد
                if message:
                    await self.send(text_data=json.dumps({
                        'message': message
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        'error': 'Message field is missing or empty'
                    }))
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Empty data received'
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
