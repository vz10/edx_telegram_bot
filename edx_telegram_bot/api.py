from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth.models import User
from models import EdxTelegramUser


class GenerateToken(APIView):
    def get(self, request):
        user_id = request.GET.get('id')
        user = get_object_or_404(User, pk=user_id)
        try:
            edx_telegram = EdxTelegramUser.objects.get(student=user)
            token = edx_telegram.hash
        except EdxTelegramUser.DoesNotExist:
            token = False
        return Response({'token': token})

    def post(self, request):
        user_id = request.POST.get('id')
        user = get_object_or_404(User, pk=user_id)
        edx_telegram, created = EdxTelegramUser.objects.get_or_create(student=user)
        return Response({'token': edx_telegram.hash})

    def put(self, request):
        user_id = request.data.get('id')
        user = get_object_or_404(User, pk=user_id)
        edx_telegram, created = EdxTelegramUser.objects.get_or_create(student=user)
        edx_telegram.hash = ""
        edx_telegram.status = EdxTelegramUser.STATUS_NEW
        edx_telegram.telegram_id = ""
        edx_telegram.save()
        return Response({'token': edx_telegram.hash})
