import calendar
from datetime import timedelta

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Count
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.template import RequestContext

import uuid
import Post
import Comment

from author.models import Authors, Friends, Posts, Comments, GithubStreams, TwitterStreams, FacebookStreams
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

import json

# TODO: Fix the template pathing using settings.py
def indexPage(request):
    return render(request, 'index/intro.html')

def redirectIndex(request):
    return redirect(indexPage)
    
def mainPage(request):

    if request.user.is_authenticated():
        
        current_user = request.user.username
        author_id = Authors.objects.get(username=current_user)
    
        items = []
        if request.method == "GET":
            for x in Posts.objects.filter(author_id=author_id).order_by("date"):
               
               items.insert(0,x)
	 
        #return render(request, 'main.html')
        return render(request,'main.html',{'items':items})

    else:

        return render(request, 'main.html')
        

def loginPage(request):
    context = RequestContext(request)

    # Handle if signin not clicked
    if len(request.POST) == 0:
        return render(request, 'login/login.html')

    username = request.POST.get('username', "").strip()
    password = request.POST.get('password', "").strip()
    error_msg = None

    # Check if fields are filled.
    if username and password:

        user = authenticate(username=username, password=password)
        print(user)
        # Determine if user exists.
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(mainPage)

            else:
                error_msg = """Account is deactivated. Please contact 
                            website hosts for further assistance."""

                return render (request, 'login/login.html', {'error_msg':error_msg })

        else:
            error_msg = "Username or password is not valid. Please try again." 
            return render (request, 'login/login.html', {'error_msg':error_msg })


    else:
        error = "Missing either a username or password. Please supply one "

    error_msg = error_msg if error else "Unknown Error."
    return render(request, 'login/login.html', {'error_msg': error_msg})

def logout(request):
    logout(request)
    return redirect(Index)
  

def friendRequest(request):
    items = []
    if request.method == 'GET':
        current_user = request.user
        print current_user.id
        #print request.user.is_authenticated()

        # if logged in
        if request.user.is_authenticated():

            for e in Friends.objects.filter(invitee_id_id=current_user.id): 
                if e.status is False :
                    a = Authors.objects.filter(author_id=e.inviter_id_id)
                    items.append(a)
        else: #do it anyway for now using ID 4 even if not logged in
        # ex: 4 has asked 3 to be their friend.
        # 	  2 has asked 3 to be their friend. Show 2 and 4 as followers of 3
            for e in Friends.objects.filter(invitee_id_id=3): 
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
        
        current_user = request.user.username
        
        author_id = Authors.objects.get(username=current_user)
        
        content = request.POST["posttext"]
        privacy = "public"
            #author_id = "heyimcameron"
      
        try:
            image=request.FILES["image"]
        except:
            image=""
        

        new_post = Posts.objects.get_or_create(author_id = author_id,content = content, image=image, privacy = privacy )

        return redirect(mainPage)

def registerPage(request):
    if request.method == 'POST':

        #print request
        error_msg = None

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
           
        new_user = User.objects.create_user(username, email, password)
        new_author = Authors.objects.get_or_create(name=name, username=username, 
            image=image, location=location, email=email, github=github, 
            facebook=facebook, twitter=twitter)

        # Successful. Redirect to Login
        return redirect(loginPage)

    else:
        
        # Render Register Page
        return render(request, 'Register.html')



      
