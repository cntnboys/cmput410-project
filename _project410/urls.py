from django.conf.urls import patterns, include, url
from django.contrib import admin

<<<<<<< HEAD
=======
import hello.views
import polls.views
>>>>>>> pro/master
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', '_project410.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

<<<<<<< HEAD
    url(r'^admin/', include(admin.site.urls)),
=======
    url(r'^$', polls.views.mainpage, name='mainpage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^hello/', hello.views.index, name='index'),
    url(r'^polls/', include('polls.urls')),
>>>>>>> pro/master
)
