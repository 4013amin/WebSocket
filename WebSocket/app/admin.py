from django.contrib import admin
from .models import Message, ChatRoom


# Register your models here.

@admin.register(Message)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['room']
