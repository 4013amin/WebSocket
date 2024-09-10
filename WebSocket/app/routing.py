from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/app/(?P<room_name>\w+)/(?P<username>\w+)/$', consumers.ChatConsumer.as_asgi()),
]

