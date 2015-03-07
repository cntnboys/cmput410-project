import calendar
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from forms import NewForm

from author.models import Authors, Friends, Posts, Comments, GithubStreams, TwitterStreams, FacebookStreams
from django.contrib.auth.models import User

# TODO: Fix the template pathing using settings.py
def indexPage(request):
    return render(request, 'index/intro.html')

def redirectIndex(request):
    return redirect(indexPage)

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
    # User is logged in
    # http://code.tutsplus.com/tutorials/building-ribbit-in-django--net-29957
    # if request.user.is_authenticated():
    #     ribbit_form = RibbitForm()
    #     user = request.user
    #     ribbits_self = Ribbit.objects.filter(user=user.id)
    #     ribbits_buddies = Ribbit.objects.filter(user__userprofile__in=user.profile.follows.all)
    #     ribbits = ribbits_self | ribbits_buddies
 
    #     return render(request,
    #                   'buddies.html',
    #                   {'ribbit_form': ribbit_form, 'user': user,
    #                    'ribbits': ribbits,
    #                    'next_url': '/', })
    # else:
    #     # User is not logged in
    #     auth_form = auth_form or AuthenticateForm()
    #     user_form = user_form or UserCreateForm()
 
    #     return render(request,
    #                   'home.html',
    #                   {'auth_form': auth_form, 'user_form': user_form, })
    return render(request, 'friendrequest.html')

def friends(request):
    return render(request, 'friends.html')


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
        email=request.POST["email"]
        github=request.POST["github"]
        facebook=request.POST["facebook"]
        twitter=request.POST["twitter"]
        location="local"

        try:
            image=request.FILES["image"]
        except:
            image=""

        if (name and username and email):

            right = 0
            if Authors.objects.filter(username=username):
               request.username = "Please choose another username"
               right = 1
               username = "Username already exists"
                #return HttpResponseRedirect('../register?username='+"Username&already&taken")
                #
               if Authors.objects.filter(email=email):
                 right = 1
                 email = "Email already exists"
           
            if right!=0:
               pass
               # DO SOMETHING

            else:
                new_author = Authors.objects.get_or_create(name=name, username=username, image=image, location=location, email=email, github=github, facebook=facebook, twitter=twitter)



    return render(request, 'Register.html')


      