import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack

# تنظیم متغیرهای محیطی برای Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebSocket.settings')

# اطمینان از تنظیم شدن Django
django.setup()

import app.routing

# تعریف application برای ASGI
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # برای درخواست‌های HTTP
    "websocket": AuthMiddlewareStack(  # برای WebSocket
        URLRouter(
            app.routing.websocket_urlpatterns  # استفاده از websocket_urlpatterns
        )
    ),
})
