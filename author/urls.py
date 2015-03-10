from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from author import views

urlpatterns = patterns('',
    url(r'^$', views.indexPage, name='IndexPage'),
    url(r'^login/$', views.loginPage, name='LoginPage'),
    url(r'^logout/$', views.logout, name="logout"),
    url(r'^register/$', views.registerPage, name='RegisterPage'),
    url(r'^profile/$', views.profileMain, name='ProfileMain'),
    url(r'^yourprofile', views.getyourProfile, name='getyourProfile'),
    url(r'^friends/(?P<userid>.*)/$', views.getaProfile, name='getaProfile'),
    url(r'^profile/Editprofile', views.editProfile, name='EditProfile'),
    url(r'^Editprofile/$', views.editProfile, name='EditProfile'),
    url(r'^registerPage/$', views.editProfile, name='registerPage'),
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
