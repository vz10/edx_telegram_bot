from django.conf.urls import include, patterns, url
from views import courses_list, course_nods
from api import GenerateToken, BotFriendlyCourseAPI

from django.conf import settings


urlpatterns = patterns(
    '',
    #Bot ape urls
    url(r'^api/generate/$', GenerateToken.as_view()),
    url(r'^api/bot_course/$', BotFriendlyCourseAPI.as_view()),

    #Bot views url
    url(r'^courses/$', courses_list),
    url(r'^courses/{}'.format(settings.COURSE_KEY_PATTERN), course_nods))


