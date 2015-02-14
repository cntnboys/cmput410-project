from django.shortcuts import render

from polls.models import Authors, Friends, Posts, Comments, GithubStreams, TwitterStreams, FacebookStreams

from django.http import HttpResponse
# Create your views here.
def index(request):
    return HttpResponse ("Hey, you're in polls.")

def mainpage(request):
    return render(request, 'mainpage.html', dirs=('templates',))
