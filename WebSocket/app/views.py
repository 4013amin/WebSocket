from django.shortcuts import render


def websocket_test(request):
    return render(request, 'index.html')
