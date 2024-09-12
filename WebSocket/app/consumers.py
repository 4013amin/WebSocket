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
            self.groups_name,  # Use groups_name here
            self.channel_name
        )
        await self.accept()

        if self.room_name in self.room_messages:
            for message_data in self.room_messages[self.room_name]:
                await self.send(text_data=json.dumps(message_data))

    async def disconnect(self, close_code):
        # Handle user disconnection
        if self.room_name in self.room_users and self.username in self.room_users[self.room_name]:
            self.room_users[self.room_name].remove(self.username)
            if not self.room_users[self.room_name]:
                del self.room_users[self.room_name]

        await self.channel_layer.group_discard(
            self.groups_name,  # Use groups_name here
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        sender = text_data_json.get('sender')
        message_type = text_data_json.get('type')
        file_content = text_data_json.get('file_content')  # Update to file_content

        message_data = {
            'message': message or file_content,  # Use file_content if message is None
            'sender': sender,
            'type': message_type
        }

        if self.room_name not in self.room_messages:
            self.room_messages[self.room_name] = []
        self.room_messages[self.room_name].append(message_data)

        await self.channel_layer.group_send(
            self.groups_name,
            {
                'type': 'chat_message',
                'message': message or file_content,  # Use file_content if message is None
                'sender': sender,
                'message_type': message_type
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        message_type = event.get('message_type', 'text')

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'type': message_type
        }))
