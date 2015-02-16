from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from polls import views

urlpatterns = patterns('',
    url(r'^$', views.mainPage, name='MainPage'),
    url(r'^login/$', views.loginPage, name='LoginPage'),
    url(r'^profile/$', views.editProfileMain, name='EditProfileMain'),
    url(r'^register/$', views.registerPage, name='RegisterPage'),
)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )