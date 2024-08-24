import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

# تنظیمات لاگ‌برداری
logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # پذیرش اتصال WebSocket
        await self.accept()
        logger.info("WebSocket connection established.")

    async def disconnect(self, close_code):
        # پایان اتصال WebSocket
        logger.info(f"WebSocket connection closed with code: {close_code}")

    async def receive(self, text_data):
        try:
            # چاپ داده‌های خام دریافتی برای بررسی
            logger.debug(f"Received raw data: {text_data}")

            # تجزیه JSON
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')

            if message:
                # ارسال پیام به کلاینت
                await self.send(text_data=json.dumps({
                    'message': message
                }))
                logger.info(f"Sent message: {message}")
            else:
                # ارسال پیام خطا در صورت وجود مشکل در داده‌ها
                await self.send(text_data=json.dumps({
                    'error': 'Message field is missing or empty'
                }))
                logger.warning("Message field is missing or empty.")

        except json.JSONDecodeError as e:
            # مدیریت خطاهای JSON
            logger.error(f"JSON Decode Error: {e}")
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))

