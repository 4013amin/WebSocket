from django.db import models
from django.contrib.auth.models import User


class ChatRoom(models.Model):
    room_name = models.CharField(max_length=255)

    def __str__(self):
        return self.room_name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}..."
