from django.urls import path
from .views import get_registered_users

urlpatterns = [
    path('api/registered_users/', get_registered_users, name='get_registered_users'),
]
