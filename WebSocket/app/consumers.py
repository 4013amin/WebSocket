import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging


class ChatConsumer(AsyncWebsocketConsumer):
    room_messages = {}

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        logging.debug(f"Connecting to room: {self.room_name}")
        logging.debug(f"Group name: {self.room_group_name}")

        # Join room group
        try:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

            # Send previous messages to new user
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
        logging.info(f"Disconnected from room: {self.room_name}")

    async def receive(self, text_data):
        if not text_data:
            return

        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            sender_username = text_data_json['sender']
        except (json.JSONDecodeError, KeyError) as e:
            logging.error(f"Error processing received message: {e}")
            return

        # Create message for sending
        message_data = {
            'message': message,
            'sender': sender_username
        }

        # Store message in temporary memory
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




class Chat_newConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.group_name = f"chat_{self.username}"  # استفاده از username برای نام گروه
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        if text_data:
            text_data_json = json.loads(text_data)
            username = text_data_json['username']

            # ارسال پیام به گروه مربوط به username
            await self.channel_layer.group_send(
                f"chat_{username}",
                {
                    'type': 'chat_message',
                    'message': text_data_json['message'],
                }
            )

    async def chat_message(self, event):
        message = event['message']
        # ارسال پیام به کلاینت
        await self.send(text_data=message)
