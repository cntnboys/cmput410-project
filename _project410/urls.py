from django.conf.urls import patterns, include, url,
from django.conf import settings
from django.contrib import admin

from django.conf.urls.static import static
import friends.views
import author.views
import friendrequest.views

from rest_framework import routers, serializers, viewsets


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


#import friends.views
import author.views
#import friendrequest.views



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', '_project410.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', include(router.urls)),
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
