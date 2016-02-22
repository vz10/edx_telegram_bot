from django.conf.urls import include, patterns, url
from views import GenerateToken

from django.conf import settings


urlpatterns = patterns(
    '', url(r'', include('lms.urls')),
    url(r'^api/bot/generate/$', GenerateToken.as_view()),
)