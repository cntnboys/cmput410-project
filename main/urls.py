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

    # Get Our Dataa
    url(r'^api/getallauthors/', views.getAllAuthors, name = 'getAllAuthors'),
    url(r'^api/getposts/', views.getposts, name='getposts'),
    url(r'^api/getfriendstatus/$', views.getfriendstatus, name='getfriendstatus'),
    url(r'^api/author/posts2/$', views.authorposts, name='authorposts'),
    url(r'^api/getapost/$', views.singlepost, name='singlepost'), 
    url(r'^api/getpostsbyauthor/$', views.getPostsByAuthor, name='postsbyauthor'),
    url(r'^api/newfriendrequest/$', views.newfriendrequest, name='newfriendrequest'),    
    url(r'^api/checkfriends/$', views.checkfriends, name='checkfriends'),
    url(r'^api/Foafvis/$', views.Foafvis, name='Foafvis'),

    # Logged In Pages
    url(r'^(?P<current_user>.+?)/posts/', views.mainPage, name='mainPage'),
    url(r'^(?P<author_name>.+?)/posts/(?P<post_uuid>.+?)/', views.onePost, name='onePost'),
    url(r'^(?P<theusername>.+?)/(?P<user_id>.+?)/', views.getaProfile, name='getaProfile'),
    url(r'^(?P<current_user>.+?)/(?P<current_userid>.+?)/edit', views.editProfile, name='EditProfile'),
    url(r'^makePost/$', views.makePost, name='makePost'),
    url(r'^editPost/$', views.editpost, name='editpost'),
    url(r'^makeComment/$', views.makeComment, name='makeComment'),
    url(r'^deletepost/$', views.deletePost, name='deletepost'),
    url(r'^searchPage/$', views.searchPage, name='SearchPage'),
    url(r'^friends/$',views.friends, name='userFriends'),
    url(r'^unfriend/$', views.unfriend, name='unfriend'),
    url(r'^unfollow/$', views.unfollow, name='unfollow'),
    url(r'^follow/$', views.follow, name='follow'),
    
)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )
