from channels.generic.websocket import AsyncWebsocketConsumer
import json

# یک دیکشنری برای نگهداری کاربران آنلاین به ازای هر اتاق
online_users_per_room = {}


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f'chat_{self.room_name}'

        # اضافه کردن کاربر به گروه
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # اضافه کردن کاربر به لیست کاربران آنلاین
        if self.room_group_name not in online_users_per_room:
            online_users_per_room[self.room_group_name] = set()
        online_users_per_room[self.room_group_name].add(self.username)

        await self.accept()

        # ارسال لیست کاربران آنلاین به کاربر جدید
        await self.send_online_users()

    async def disconnect(self, close_code):
        # حذف کاربر از گروه
        pass
        # await self.channel_layer.group_discard(
        #     self.room_group_name,
        #     self.channel_name
        # )

        # حذف کاربر از لیست کاربران آنلاین
        if self.room_group_name in online_users_per_room:
            online_users_per_room[self.room_group_name].discard(self.username)
            if not online_users_per_room[self.room_group_name]:
                del online_users_per_room[self.room_group_name]

        # ارسال لیست کاربران آنلاین به سایر کاربران
        await self.send_online_users()

    async def send_online_users(self):
        # ارسال لیست کاربران آنلاین به گروه
        users = list(online_users_per_room.get(self.room_group_name, []))
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'online_users',
                'users': users
            }
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')

        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': self.username
                }
            )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    async def online_users(self, event):
        users = event['users']
        await self.send(text_data=json.dumps({
            'online_users': users
        }))
