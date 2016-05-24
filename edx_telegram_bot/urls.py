from django.conf.urls import include, patterns, url
from views import courses_list, course_nods
from api import GenerateToken, BotFriendlyCourseAPI

from django.conf import settings


urlpatterns = patterns(
    '', url(r'', include('lms.urls')),
    #Bot ape urls
    url(r'^api/bot/generate/$', GenerateToken.as_view()),
    url(r'^api/bot/bot_course/$', BotFriendlyCourseAPI.as_view()),

    #Bot views url
    url(r'^bot/courses/$', courses_list),
    url(r'^bot/courses/{}'.format(settings.COURSE_KEY_PATTERN), course_nods))

