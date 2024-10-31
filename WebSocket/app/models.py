from django.db import models


class ChatRoom(models.Model):
    room_name = models.CharField(max_length=255, unique=True)


class Message(models.Model):
    user = models.CharField(max_length=255)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class VoiceMessage(models.Model):
    user = models.CharField(max_length=255)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    voice_data = models.TextField()  # ذخیره داده صوتی به عنوان رشته Base64
    timestamp = models.DateTimeField(auto_now_add=True)
