from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import main.views

handler404 = 'main.views.custom404'

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', '_project410.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', main.views.redirectIndex, name='IndexPage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^friends/', main.views.friends, name='friends'),
    url(r'^main/', include('main.urls')),
    url(r'^friendrequest/', main.views.friendRequest, name='friendRequest'),
    url(r'^searchPage/', main.views.searchPage, name='SearchPage'),
    url(r'^friends/(?P<userid1>\w{0,50})/(?P<userid2>\w{0,50})$', main.views.foaf, name='foaf'),
    #urlpatterns += staticfiles_urlpatterns(),
    #url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': settings.DEBUG}),


)+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += patterns(
            'django.views.static',
            (r'media/(?P<path>.*)',
            'serve',
            {'document_root': settings.MEDIA_ROOT}), )

if not settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}),
    )