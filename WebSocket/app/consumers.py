from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging


class ChatConsumer(AsyncWebsocketConsumer):
    # حافظه موقت برای ذخیره پیام‌ها
    room_messages = {}

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        logging.debug(f"Attempting to connect to room: {self.room_name}")
        logging.debug(f"Group name: {self.room_group_name}")

        # Join room group
        try:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

            # ارسال پیام‌های قبلی به کاربر جدید
            if self.room_name in self.room_messages:
                for message_data in self.room_messages[self.room_name]:
                    await self.send(text_data=json.dumps(message_data))

            logging.info(f"Connection accepted for room: {self.room_name}")
        except Exception as e:
            logging.error(f"Error connecting to WebSocket: {e}")
            await self.close()

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
            logging.error("Invalid message format")
            return

        message_data = {
            'message': message,
            'sender': sender_username
        }

        # Store message and broadcast to the group
        self.room_messages.setdefault(self.room_name, []).append(message_data)

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
