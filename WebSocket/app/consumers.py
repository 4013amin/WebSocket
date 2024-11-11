import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message, ImageMessage


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
        print(f'User {self.username} connected to {self.room_name}')

        # Retrieve previous text messages
        previous_messages = await self.get_previous_messages()
        for message in previous_messages:
            await self.send(text_data=json.dumps({
                'sender': message.user,
                'message': message.content,
                'timestamp': str(message.timestamp)
            }))

        # Retrieve previous images
        previous_images = await self.get_previous_images()
        for image in previous_images:
            await self.send(text_data=json.dumps({
                'sender': image.user,
                'image_data': image.image_data,
                'timestamp': str(image.timestamp)
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f'User {self.username} disconnected from {self.room_name}')

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                text_data_json = json.loads(text_data)
                message = text_data_json.get('message')
                image_data = text_data_json.get('image_data')

                if message:
                    # Save and send text message
                    await self.save_chat_message(self.username, message)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': message,
                            'sender': self.username
                        }
                    )
                elif image_data:
                    # Save and send image message
                    await self.save_image_message(self.username, image_data)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'image_message',
                            'image_data': image_data,
                            'sender': self.username
                        }
                    )
                else:
                    await self.send(text_data=json.dumps({
                        'error': 'No valid content provided'
                    }))
            except json.JSONDecodeError as e:
                await self.send(text_data=json.dumps({
                    'error': f'JSON decode error: {str(e)}'
                }))
            except Exception as e:
                await self.send(text_data=json.dumps({
                    'error': f'Failed to process message: {str(e)}'
                }))
        else:
            await self.send(text_data=json.dumps({
                'error': 'No data received'
            }))

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    async def image_message(self, event):
        image_data = event['image_data']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'image_data': image_data,
            'sender': sender
        }))

    @database_sync_to_async
    def save_chat_message(self, username, content):
        room, _ = ChatRoom.objects.get_or_create(room_name=self.room_name)
        Message.objects.create(user=username, room=room, content=content)

    @database_sync_to_async
    def save_image_message(self, username, image_data):
        room, _ = ChatRoom.objects.get_or_create(room_name=self.room_name)
        ImageMessage.objects.create(user=username, room=room, image_data=image_data)

    @database_sync_to_async
    def get_previous_messages(self):
        room, _ = ChatRoom.objects.get_or_create(room_name=self.room_name)
        return list(Message.objects.filter(room=room).order_by('timestamp'))

    @database_sync_to_async
    def get_previous_images(self):
        room, _ = ChatRoom.objects.get_or_create(room_name=self.room_name)
        return list(ImageMessage.objects.filter(room=room).order_by('timestamp'))

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
