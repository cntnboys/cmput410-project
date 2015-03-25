from django.contrib import admin

from main.models import Authors, Friends, Posts, Comments, GithubStreams 

# Register your models here.

admin.site.register(Authors)
admin.site.register(Friends)
admin.site.register(Posts)
admin.site.register(Comments)
admin.site.register(GithubStreams)
