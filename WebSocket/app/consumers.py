import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Users  # Assuming your model is in models.py

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.username = self.scope['url_route']['kwargs']['username']

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Save the user to the database
        try:
            await self.save_message(self.username)
        except ValueError as e:
            # Handle the case where the user already exists
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
            return

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = self.scope['url_route']['kwargs']['username']

        # Send message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @database_sync_to_async
    def save_message(self, username):
        try:
            user = User.objects.get(username=username)
            if Users.objects.filter(username=user).exists():
                raise ValueError(f"User '{username}' has already been saved.")
            Users.objects.create(username=user)
        except User.DoesNotExist:
            raise ValueError(f"User '{username}' does not exist.")
