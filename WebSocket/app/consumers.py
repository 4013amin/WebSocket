class ChatConsumer(AsyncWebsocketConsumer):
    async def receive(self, text_data):
        try:
            logger.debug(f"Received raw data: {text_data}")

            # تجزیه JSON
            text_data_json = json.loads(text_data)
            content = text_data_json.get('content', '')  # تغییر به "content"

            if content:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'content': content  # تغییر به "content"
                    }
                )
                logger.info(f"Broadcasted message in room {self.room_name}: {content}")
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Message field is missing or empty'
                }))
                logger.warning("Message field is missing or empty.")

        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {e}")
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))

    async def chat_message(self, event):
        content = event['content']  # تغییر به "content"

        await self.send(text_data=json.dumps({
            'message': content  # تغییر به "message"
        }))
