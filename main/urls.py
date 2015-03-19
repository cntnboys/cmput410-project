from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from main import views

# Django Dynamic URL Tokens by werehuman were used to model urls in the project 
# (http://stackoverflow.com/questions/21693357/django-dynamic-page-functionality-and-url)

urlpatterns = patterns('',
    url(r'^$', views.indexPage, name='IndexPage'),
    url(r'^login/$', views.loginPage, name='LoginPage'),
    url(r'^logout/$', views.logout, name="logout"),
    url(r'^register/$', views.registerPage, name='RegisterPage'),
    url(r'^(?P<current_user>.+?)/posts/', views.mainPage, name='mainPage'),

    url(r'^getauthors/$', views.getauthors, name='getauthors'),
    url(r'^getfriends/$', views.getfriends, name='getfriends'),
    url(r'^getposts/$', views.getposts, name='getposts'),   
    url(r'^getcomments/$', views.getcomments, name='getcomments'),
    url(r'^getgithub/$', views.getgithub, name='getgithub'),



    url(r'^(?P<theusername>.+?)/(?P<user_id>.+?)/$', views.getaProfile, name='getaProfile'),
    url(r'^(?P<current_user>.+?)/(?P<current_userid>.+?)/edit', views.editProfile, name='EditProfile'),
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