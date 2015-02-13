from django.contrib import admin

from polls.models import Authors, Friends, Posts, Comments, GithubStreams, TwitterStreams, FacebookStreams

# Register your models here.

admin.site.register(Authors)
admin.site.register(Friends)
admin.site.register(Posts)
admin.site.register(Comments)
admin.site.register(GithubStreams)
admin.site.register(TwitterStreams)
admin.site.register(FacebookStreams)