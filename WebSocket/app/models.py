from django.db import models


class ChatRoom(models.Model):
    room_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.room_name


class Message(models.Model):
    user = models.CharField(max_length=255)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}: {self.content}'


class VoiceMessage(models.Model):
    user = models.CharField(max_length=255)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    voice_data = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - Voice Message at {self.timestamp}'
