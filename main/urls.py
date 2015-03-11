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
    url(r'^(?P<current_user>.+?)/(?P<current_userid>.+?)', views.getyourProfile, name='getyourProfile'),
    url(r'^(?P<theusername>.+?)/(?P<user_id>.+?)', views.getaProfile, name='getaProfile'),
    url(r'^(?P<current_user>.+?)/(?P<current_userid>.+?)/edit', views.editProfile, name='EditProfile'),
    url(r'^makePost/$', views.makePost, name='makePost'),
    url(r'^searchPage/$', views.searchPage, name='SearchPage'),
    url(r'^friends/$',views.friends, name='userFriends')
    
)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )
