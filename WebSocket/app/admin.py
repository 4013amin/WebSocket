from django.contrib import admin
from .models import Message, VoiceMessage, ImageMessage


# Register your models here.

@admin.register(Message)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['room']


@admin.register(VoiceMessage)
class VoiceMessageAdmin(admin.ModelAdmin):
    list_display = ['room']


@admin.register(ImageMessage)
class ImageMessageAdmin(admin.ModelAdmin):
    list_display = ['room']
