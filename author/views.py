import calendar
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from forms import NewForm
import uuid

from author.models import Authors, Friends, Posts, Comments, GithubStreams, TwitterStreams, FacebookStreams
from django.contrib.auth.models import User

from django.db.models import Count

import json

# TODO: Fix the template pathing using settings.py
def indexPage(request):
    return render(request, 'index/intro.html')

def redirectIndex(request):
    return redirect(indexPage)
    
def mainPage(request):
    return render(request, 'main.html')

def loginPage(request):
    # TODO: Fix this Login Request
    context = RequestContext(request)

    # Handle if signin not clicked
    if len(request.POST) == 0:
        return render(request, 'login/login.html')

    username = request.POST.get('username', None).strip()
    password = request.POST.get('username', None).strip()
    error_msg = None

    # Check if fields are filled.
    if username and password:

        # Determine if user exists.
        try:
            user = Authors.objects.get(username=username)
        except ObjectDoesNotExist:
            error_msg = "User %s does not exist" % username
            return render (request, 'login/login.html', {'error_msg':error_msg})

        if user.password == password:
            response = render_to_response('index/intro.html',
                        {'password': password, 'username': username }, 
                        RequestContext(request))

            return response

        else:
            error = "Password Incorrect. Please Try Again."
    else:
        error = "Missing either a username or password. Please supply one "

    error_msg = error_msg if error else "Unknown Error."
    return render(request, 'login/login.html', {'error_msg': error_msg})
  

def friendRequest(request):

    return render(request, 'friendrequest.html')

def friends(request):
    # links = Authors.objects.all()
    # context = RequestContext(request)
    # return render_to_response('friends.html',{'links': links}, context)
    #json.loads(request.POST.get('JSONreponseobj', '{}'))
    items = []
    JSONobj = {}
    if request.method == 'GET':
        #context = RequestContext(request)
        #links = Friends.objects.all()
        #for x in q.count():
            #print Friends.objects.filter(invitee_id_id)
        c = 0
        for e in Friends.objects.filter(inviter_id_id=1):
            #print(e.invitee_id_id)
            a = Authors.objects.filter(author_id=e.invitee_id_id)
            #links = q
            print a.values('name')
            print a.values('username')
            print a.values('image')
            items[c] = a

            #JSONobj['qname'] = q.values('name')
            #JSONobj['quser'] = q.values('username')
            #JSONobj['qimage'] = q.values('image')
            #print JSONobj.qname
            #names.append(q[0].name)
            #users.append(q[0].username)
            #images.append(q[0].image)

            #print names, users, images
            c = c + 1

            #JSONreponseobj.push(name,user,image)
            #return render_to_response('friends.html',{'name':qname, 'username':quser, 'image':qimage}, context)
        #allList = [names, users, images]
        #Friends.objects.filter(inviter_id_id=)
    #return render(request, 'friends.html')
    #print JSONreponseobj
    #my_list = list(self.get_queryset().values_list('code', flat=True))

    #json_data = json.dumps(JSONobj)
    #return render(request, 'friends.html',{'names':names, 'users':users, 'images':images})
    #q = a
    return render(request, 'friends.html',{'items':items})


def profileMain(request):
    return render(request, 'profile.html')

def editProfile(request):
    return render(request, 'Editprofile.html')

def registerPage(request):
    if request.method== 'POST':

        print request
        error = None

        name=request.POST["name"]
        username=request.POST["username"]
        password=request.POST["password"]
        email=request.POST["email"]
        github=request.POST["github"]
        facebook=request.POST["facebook"]
        twitter=request.POST["twitter"]
        location="bubble"

        try:
            image=request.FILES["image"]
        except:
            image=""

        if Authors.objects.filter(username=username):
            error_msg = "Username already exists"
            return render (request, 'Register.html', {'error_msg':error_msg, 'name':name, 'username':username, 'email':email, 'image':image, 'github':github, 'facebook':facebook, 'twitter':twitter})

        if Authors.objects.filter(email=email):
            error_msg = "Email already exists"
            return render (request, 'Register.html', {'error_msg':error_msg, 'name':name, 'username':username, 'email':email, 'github':github, 'facebook':facebook, 'twitter':twitter})
           



        new_author = Authors.objects.get_or_create(name=name, username=username, image=image, location=location, email=email, github=github, facebook=facebook, twitter=twitter)




    return render(request, 'Register.html')


      