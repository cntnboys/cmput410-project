from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from django.conf.urls.static import static
import friends.views
import author.views
import friendrequest.views

from rest_framework import routers, serializers, viewsets

#import friends.views
import author.views
#import friendrequest.views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', '_project410.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', author.views.redirectIndex, name='IndexPage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^friends/', author.views.friends, name='friends'),
    url(r'^author/', include('author.urls')),
    url(r'^friendrequest/', author.views.friendRequest, name='friendRequest'),
    url(r'^main/', author.views.mainPage, name='mainPage'),
    
)+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )
