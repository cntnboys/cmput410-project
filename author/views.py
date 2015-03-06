import calendar
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.forms import EmailField
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib import messages

from forms import NewForm

from author.models import Authors, Friends, Posts, Comments, GithubStreams, TwitterStreams, FacebookStreams


# TODO: Fix the template pathing using settings.py
def mainPage(request):
	return render(request, 'intro.html')

def redirectMain(request):
	return redirect(mainPage)

def loginPage(request):
	return render(request, 'login.html')

def home(request):
	return render(request, 'main.html')

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

def homePage(request):
	return render(request, 'homepage.html')

def index(request):
	return render(request, 'index.html')

def userlogin(request):
	context = RequestContext(request)
	
	error = None
	
	if request.method == 'POST':
		username = request.POST.get("username","").strip()
		print(username)
		password = request.POST.get("password","").strip()
		print(password)
		if username != "admin" or password != "admin":
			error = "Invalid username or password"
			return HttpResponseRedirect('../login')
		else:
			return HttpResponseRedirect('../homepage')
	else:
		return render(request, 'login.html')        