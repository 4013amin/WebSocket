from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .serializer import UserSerializer
from django.http import JsonResponse
from .models import Users


def get_registered_users(request):
    users = Users.objects.all().values('username__username', 'created_at')
    user_list = list(users)
    return JsonResponse(user_list, safe=False)
