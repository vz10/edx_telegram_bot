from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth.models import User

from models import EdxTelegramUser


class GenerateToken(APIView):
    def post(self, request):
        user_id = request.POST.get('id')
        user = get_object_or_404(User, pk=user_id)
        edx_telegram = EdxTelegramUser.get_or_create(user=user)

        return Response({'token': edx_telegram.token})

