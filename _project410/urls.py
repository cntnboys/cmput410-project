from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from polls import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', '_project410.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^$', views.redirectMain, name='MainPage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^polls/', include('polls.urls')),

)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )