import re

from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from models import EdxTelegramUser, BotFriendlyCourses, TelegramBot


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


class BotFriendlyCourseAPI(APIView):
    def get(self, request):
        course_key = re.search(settings.COURSE_KEY_PATTERN, request.query_params.get('key')[7:]).group(0)
        bot = BotFriendlyCourses.objects.filter(course_key=course_key).exists()
        bot_name = None
        if bot:
            bot_name = BotFriendlyCourses.objects.filter(course_key=course_key).first().bot.bot_name
        return Response({'bot': bot,
                         'bot_name': bot_name})

    def post(self, request):
        course_key = re.search(settings.COURSE_KEY_PATTERN, request.data['key'][7:]).group(0)
        using_bots = BotFriendlyCourses.objects.all().values_list('bot', flat=True)
        free_bot = TelegramBot.objects.all().exclude(id__in=using_bots).first()
        if free_bot:
            BotFriendlyCourses.objects.get_or_create(course_key=course_key, bot=free_bot)
            return Response({'bot': True, 'bot_name':free_bot.bot_name})
        else:
            no_free_bot = _("There is no free bot at that time, please try again later")
            return HttpResponse(no_free_bot, status=500)

    def delete(self, request):
        course_key = re.search(settings.COURSE_KEY_PATTERN, request.data['key'][7:]).group(0)
        BotFriendlyCourses.objects.filter(course_key=course_key).delete()
        return Response({'bot': False})
