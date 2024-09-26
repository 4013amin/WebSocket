import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message

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

        # Accept the WebSocket connection
        await self.accept()

        # Save user in the database (if necessary)
        try:
            await self.save_user(self.username)
        except ValueError as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
            return

        # Retrieve previous messages
        previous_messages = await self.get_previous_messages()
        for message in previous_messages:
            await self.send(text_data=json.dumps({
                'message': message.content,
                'username': message.user.username,
                'timestamp': str(message.timestamp)
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')

        if not message:
            await self.send(text_data=json.dumps({
                'error': 'No message content'
            }))
            return

        try:
            await self.save_chat_message(self.username, message)
        except ValueError as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @database_sync_to_async
    def save_user(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValueError(f"User '{username}' does not exist.")

    @database_sync_to_async
    def save_chat_message(self, username, content):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValueError(f"User '{username}' does not exist.")

        room, _ = ChatRoom.objects.get_or_create(room_name=self.room_name)

        # Save message
        Message.objects.create(user=user, room=room, content=content)

    @database_sync_to_async
    def get_previous_messages(self):
        room = ChatRoom.objects.get(room_name=self.room_name)
        return list(Message.objects.select_related('user').filter(room=room).order_by('timestamp'))


# ................................................................................
#

# for VoiceChat

# class VoiceChatConsumer(AsyncWebsocketConsumer):
#     connected_users = {}  # برای نگه‌داشتن کاربران متصل
#
#     async def connect(self):
#         self.username = self.scope['url_route']['kwargs']['username']
#         VoiceChatConsumer.connected_users[self.username] = self.channel_name
#
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         if self.username in VoiceChatConsumer.connected_users:
#             del VoiceChatConsumer.connected_users[self.username]
#
#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message_type = data['message'].get('type')
#         target_user = data.get('target_user')
#
#         if message_type == 'offer':
#             await self.handle_offer(data['message'], target_user)
#         elif message_type == 'answer':
#             await self.handle_answer(data['message'], target_user)
#         elif message_type == 'candidate':
#             await self.handle_candidate(data['message'], target_user)
#
#     async def handle_offer(self, offer, target_user):
#         if target_user in VoiceChatConsumer.connected_users:
#             await self.channel_layer.send(
#                 VoiceChatConsumer.connected_users[target_user],
#                 {
#                     'type': 'voice_offer',
#                     'offer': offer
#                 }
#             )
#         else:
#             await self.send(text_data=json.dumps({
#                 'message': 'Target user is not available.'
#             }))
#
#     async def handle_answer(self, answer, target_user):
#         if target_user in VoiceChatConsumer.connected_users:
#             await self.channel_layer.send(
#                 VoiceChatConsumer.connected_users[target_user],
#                 {
#                     'type': 'voice_answer',
#                     'answer': answer
#                 }
#             )
#
#     async def handle_candidate(self, candidate, target_user):
#         if target_user in VoiceChatConsumer.connected_users:
#             await self.channel_layer.send(
#                 VoiceChatConsumer.connected_users[target_user],
#                 {
#                     'type': 'voice_candidate',
#                     'candidate': candidate
#                 }
#             )
#
#     async def voice_offer(self, event):
#         await self.send(text_data=json.dumps({'message': event['offer']}))
#
#     async def voice_answer(self, event):
#         await self.send(text_data=json.dumps({'message': event['answer']}))
#
#     async def voice_candidate(self, event):
#         await self.send(text_data=json.dumps({'message': event['candidate']}))
