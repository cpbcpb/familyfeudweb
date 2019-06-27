from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ ws/display/$', consumers.DisplayConsumer),
    url(r'^ws/display_answer/$', consumers.DisplayAnswerConsumer),
]