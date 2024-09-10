import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    room_messages = {}
    room_users = {}

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.groups_name = f"chat_{self.room_name}"
        self.username = self.scope['url_route']['kwargs']['username']  # Getting the username

        if self.room_name not in self.room_users:
            self.room_users[self.room_name] = []
        self.room_users[self.room_name].append(self.username)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        if self.room_name in self.room_messages:
            for message_data in self.room_messages[self.room_name]:
                await self.send(text_data=json.dumps(message_data))

    async def disconnect(self, close_code):
        # Handle user disconnection
        pass

    async def receive(self, text_data):
        # Handle receiving and broadcasting chat messages
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        sender = text_data_json.get('sender')

        message_data = {
            'message': message,
            'sender': sender
        }
        if self.room_name not in self.room_messages:
            self.room_messages[self.room_name] = []
        self.room_messages[self.room_name].append(message_data)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
