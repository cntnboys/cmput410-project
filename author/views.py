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
import Post
import Comment

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
    
    items = []
    if request.method == "GET":
       for x in Posts.objects.all():		
           items.insert(0,x)
	 

    return render(request,'main.html',{'items':items})
        

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
    items = []
    if request.method == 'GET':
        current_user = request.user
        print current_user.id
        #print request.user.is_authenticated()

        # if logged in
        if request.user.is_authenticated():
            for e in Friends.objects.filter(inviter_id_id=current_user.id): 
                if e.status is False :
                    a = Authors.objects.filter(author_id=e.invitee_id_id)
                    items.append(a)
                #print a.values('name')

            for e in Friends.objects.filter(invitee_id_id=current_user.id): 
                if e.status is False :
                    a = Authors.objects.filter(author_id=e.inviter_id_id)
                    items.append(a)
        else: #do it anyway for now using ID 4 even if not logged in
            for e in Friends.objects.filter(inviter_id_id=4): 
                if e.status is False :
                    a = Authors.objects.filter(author_id=e.invitee_id_id)
                    items.append(a)

            for e in Friends.objects.filter(invitee_id_id=4): 
                if e.status is False :
                    a = Authors.objects.filter(author_id=e.inviter_id_id)
                    items.append(a)

    return render(request, 'friendrequest.html',{'items':items})

def friends(request):

    items = []
    if request.method == 'GET':
        current_user = request.user
        print current_user.id
        #print request.user.is_authenticated()

        # if logged in
        if request.user.is_authenticated():
            for e in Friends.objects.filter(inviter_id_id=current_user.id): 
                if e.status is True :
                    a = Authors.objects.filter(author_id=e.invitee_id_id)
                    items.append(a)
                #print a.values('name')

            for e in Friends.objects.filter(invitee_id_id=current_user.id): 
                if e.status is True :
                    a = Authors.objects.filter(author_id=e.inviter_id_id)
                    items.append(a)
        else: #do it anyway for now using ID 1 even if not logged in
            for e in Friends.objects.filter(inviter_id_id=1): 
                if e.status is True:
                    a = Authors.objects.filter(author_id=e.invitee_id_id)
                    items.append(a)

            for e in Friends.objects.filter(invitee_id_id=1): 
                if e.status is True :
                    a = Authors.objects.filter(author_id=e.inviter_id_id)
                    items.append(a)

    return render(request, 'friends.html',{'items':items})


def profileMain(request):
    return render(request, 'profile.html')

def editProfile(request):
    return render(request, 'Editprofile.html')



def makePost(request):
    if request.method == "POST":
        
        
        content = request.POST["posttext"]
        image   = request.FILES["image"]
        privacy = "public"
        author_id = "heyimcameron"

        new_post = Posts.objects.get_or_create(author_id = author_id,content = content, image=image, privacy = privacy )

        return redirect(mainPage)


        

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


      
