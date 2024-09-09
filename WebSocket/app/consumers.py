import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    room_messages = {}
    room_users = {}

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.username = self.scope['url_route']['kwargs']['username']

        # Initialize room_users for the room if not present
        if self.room_name not in self.room_users:
            self.room_users[self.room_name] = []

        # Add the new user to the room
        user = {'username': self.username}
        self.room_users[self.room_name].append(user)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Send the updated user list to all clients in the room
        await self.send_user_list()

        # Optionally, send existing messages to the newly connected user
        if self.room_name in self.room_messages:
            for message_data in self.room_messages[self.room_name]:
                await self.send(text_data=json.dumps(message_data))

    async def disconnect(self, close_code):
        # Remove the user from the room_users list
        self.room_users[self.room_name] = [
            user for user in self.room_users[self.room_name]
            if user['username'] != self.username
        ]

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Send the updated user list to all clients in the room
        await self.send_user_list()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')

        if message_type == 'chat_message':
            await self.handle_chat_message(text_data_json)
        elif message_type == 'user_list':
            await self.handle_user_list(text_data_json)
        else:
            await self.send(text_data=json.dumps({
                'error': 'Unknown message type'
            }))

    async def handle_chat_message(self, data):
        message = data.get('message')
        sender = data.get('sender')

        message_data = {
            'type': 'chat_message',
            'message': message,
            'sender': sender
        }

        # Initialize room_messages for the room if not present
        if self.room_name not in self.room_messages:
            self.room_messages[self.room_name] = []
        self.room_messages[self.room_name].append(message_data)

        # Broadcast the message to all clients in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            message_data
        )

    async def handle_user_list(self, data):
        # Handle the user list message if needed
        # In most cases, you might not need to handle this on the server side.
        # The `send_user_list` method is primarily for broadcasting updates to all clients.
        pass

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender': sender
        }))

    async def send_user_list(self):
        user_list_data = {
            'type': 'user_list',
            'users': self.room_users.get(self.room_name, [])
        }
        await self.channel_layer.group_send(
            self.room_group_name,
            user_list_data
        )
