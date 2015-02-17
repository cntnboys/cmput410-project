from django.conf.urls import patterns, url
from friendrequest import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
)