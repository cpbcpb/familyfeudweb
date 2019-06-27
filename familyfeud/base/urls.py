from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.button, name='button'),
    url(r'^hello/$', views.helloworld, name='helloworld'),
    url(r'^questions/$', views.questions, name='questions'),
    url(r'^admin/questions/$', views.adminquestions, name='adminquestions'),
    url(r'^admin/games/$', views.gamelist, name='gamelist'),
    url(r'^admin/addWrong/$', views.addWrong, name='addWrong'),
    url(r'^admin/createGame/$', views.createNewGame, name='addGame'),
    url(r'^admin/nextQuestion/$', views.nextQuestion, name='nextQuestion'),
    url(r'^admin/displayAnswer/$', views.displayAnswer, name='displayAnswer'),
    url(r'^admin/awardPoints/$', views.awardPoints, name='awardPoints'),
    url(r'^admin/revealBoard/$', views.revealBoard, name='revealBoard'),
    url(r'^admin/hideBoard/$', views.hideBoard, name='hideBoard')
]