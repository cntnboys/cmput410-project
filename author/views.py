import calendar
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError

import uuid
import Post
import Comment

from author.models import Authors, Friends, Posts, Comments, GithubStreams, TwitterStreams, FacebookStreams
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

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
    context = RequestContext(request)

    # Handle if signin not clicked
    if len(request.POST) == 0:
        return render(request, 'login/login.html')

    username = request.POST.get('username', None).strip()
    password = request.POST.get('username', None).strip()
    error_msg = None

    # Check if fields are filled.
    if username and password:

        user = authenticate(username=username, password=password)

        # Determine if user exists.
        if user is not None:
            if user.is_active:
                login(request, user);

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
  

def friendRequest(request):

    return render(request, 'friendrequest.html')

def friends(request):
    # links = Authors.objects.all()
    # context = RequestContext(request)
    # return render_to_response('friends.html',{'links': links}, context)
    #json.loads(request.POST.get('JSONreponseobj', '{}'))
    names = []
    users = []
    images = []
    if request.method == 'GET':
        context = RequestContext(request)
        #links = Friends.objects.all()
        #for x in q.count():
            #print Friends.objects.filter(invitee_id_id)
        count = 0
        for e in Friends.objects.filter(inviter_id_id=1):
            print(e.invitee_id_id)
            q = Authors.objects.filter(author_id=e.invitee_id_id)
            links = q
            print q.values('name', 'username', 'image')
            # JSONreponseobj['qname'] = q[0].name
            # JSONreponseobj['quser'] = q[0].username
            # JSONreponseobj['qimage'] = q[0].image
            names.append(q[0].name)
            users.append(q[0].username)
            images.append(q[0].image)
            count = count + 1

            #JSONreponseobj.push(name,user,image)
            #return render_to_response('friends.html',{'name':qname, 'username':quser, 'image':qimage}, context)
        allList = [names, users, images]
        #Friends.objects.filter(inviter_id_id=)
    #return render(request, 'friends.html')
    #print JSONreponseobj
    return render_to_response('friends.html',allList, context)


def profileMain(request):
    return render(request, 'profile.html')

def editProfile(request):
    return render(request, 'Editprofile.html')



def makePost(request):
    if request.method == "POST":
<<<<<<< HEAD

=======
        
>>>>>>> 13660d8247781ed5abed40b98db8bc3e355c1f28
        
        content = request.POST["posttext"]
        image   = request.FILES["image"]
        privacy = "public"
        author_id = "heyimcameron"

        new_post = Posts.objects.get_or_create(author_id = author_id,content = content, image=image, privacy = privacy )

        return redirect(mainPage)

<<<<<<< HEAD
=======


def getPosts(request):
    #if request.method == "GET":
        #context = RequestContext(request)

   # for e in Posts.all():

        #make new Post object

       # self.title = title
       # self.post_id = post_id
       # self.post_uuid = post_uuid
      #  self.author_id = author_id
      #  self.content = content
      #  self.image = image
      #  self.privacy = privacy
      #  self.date = date
        
   return     
        




>>>>>>> 13660d8247781ed5abed40b98db8bc3e355c1f28
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
           
        new_user = User.objects.create(username=username, password=password)
        new_author = Authors.objects.get_or_create(name=name, username=username, 
            image=image, location=location, email=email, github=github, 
            facebook=facebook, twitter=twitter)

        # Successful. Redirect to Login
        return redirect(loginPage)

    else:
        
        # Render Register Page
        return render(request, 'Register.html')



      
