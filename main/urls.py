from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from main import views

urlpatterns = patterns('',
    url(r'^$', views.indexPage, name='IndexPage'),
    url(r'^login/$', views.loginPage, name='LoginPage'),
    url(r'^logout/$', views.logout, name="logout"),
    url(r'^register/$', views.registerPage, name='RegisterPage'),
    url(r'^(?P<current_user>.+?)/posts/', views.mainPage, name='mainPage'),
    url(r'^junkdata/$', views.profileMain, name='ProfileMain'),
    url(r'^(?P<user_id>.+?)/profile/$', views.getaProfile, name='getaProfile'),
    url(r'^(?P<current_user>.+?)/profile', views.getyourProfile, name='getyourProfile'),
    url(r'^(?P<current_user>.+?)/profile/edit', views.editProfile, name='EditProfile'),
    url(r'^makePost/$', views.makePost, name='makePost'),
    url(r'^searchPage/$', views.searchPage, name='SearchPage'),
    url(r'^friends/$',views.friends, name='userFriends'),
    url(r'^friendRequest/$', views.friendRequest, name='friendRequest'),
    
)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )
