from django.conf.urls import patterns, urls
from hello import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
)