from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .serializer import UserSerializer


# def websocket_test(request):
#     return render(request, 'index.html')


class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        users = User.objects.all()  # لیست تمام کاربران
        serializer = UserSerializer(users, many=True)  # سریال کردن لیست کاربران
        return Response(serializer.data)  # بازگشت لیست کاربران به صورت JSON
