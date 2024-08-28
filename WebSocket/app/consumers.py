import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    # حافظه موقت برای ذخیره پیام‌ها
    room_messages = {}

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

        # ارسال پیام‌های قبلی به کلاینت جدید (اختیاری)
        messages = self.room_messages.get(self.room_name, [])
        for message in messages:
            await self.send(text_data=json.dumps(message))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        if not text_data:
            return

        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            sender_username = text_data_json['sender']
        except (json.JSONDecodeError, KeyError):
            return

        # ایجاد پیام برای ارسال
        message_data = {
            'message': message,
            'sender': sender_username
        }

        # ذخیره پیام در حافظه موقت
        if self.room_name not in self.room_messages:
            self.room_messages[self.room_name] = []
        self.room_messages[self.room_name].append(message_data)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
