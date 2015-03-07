from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from author import views

urlpatterns = patterns('',
    url(r'^$', views.indexPage, name='IndexPage'),
    url(r'^login/$', views.loginPage, name='LoginPage'),
    url(r'^register/$', views.registerPage, name='RegisterPage'),
    url(r'^profile/$', views.profileMain, name='ProfileMain'),
    url(r'^profile/Editprofile', views.editProfile, name='EditProfile'),
    url(r'^Editprofile/$', views.editProfile, name='EditProfile'),
    url(r'^registerPage/$', views.editProfile, name='registerPage'),
)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )