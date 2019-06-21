from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.button, name='button'),
    url(r'^hello/$', views.helloworld, name='helloworld'),
    url(r'^questions/$', views.questions, name='questions'),
    url(r'^questions/admin/$', views.adminquestions, name='adminquestions'),
]