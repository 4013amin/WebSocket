import random
import json  # وارد کردن ماژول json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    # حافظه موقت برای ذخیره پیام‌ها و کاربران
    room_messages = {}
    room_users = {}

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.username = self.scope['url_route']['kwargs']['username']  # گرفتن نام کاربر

        # اضافه کردن کاربر به لیست کاربران اتاق
        if self.room_name not in self.room_users:
            self.room_users[self.room_name] = []
        self.room_users[self.room_name].append(self.username)

        # اتصال کاربر به گروه اتاق
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # ارسال پیام‌های قبلی به کاربر جدید
        if self.room_name in self.room_messages:
            for message_data in self.room_messages[self.room_name]:
                await self.send(text_data=json.dumps(message_data))

    async def disconnect(self, close_code):
        # حذف کاربر از لیست کاربران اتاق
        self.room_users[self.room_name].remove(self.username)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # اگر درخواست برای پیدا کردن کاربر تصادفی باشد
        if text_data == 'find_random_user':
            random_user = self.get_random_user()
            if random_user:
                await self.send(text_data=json.dumps({
                    'action': 'random_user_found',
                    'user': random_user
                }))
            return

        # دریافت پیام چت
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        sender = text_data_json.get('sender')

        # ذخیره پیام
        message_data = {
            'message': message,
            'sender': sender
        }
        if self.room_name not in self.room_messages:
            self.room_messages[self.room_name] = []
        self.room_messages[self.room_name].append(message_data)

        # ارسال پیام به گروه
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender
            }
        )

    def get_random_user(self):
        if self.room_users[self.room_name]:
            return random.choice(self.room_users[self.room_name])
        return None

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
