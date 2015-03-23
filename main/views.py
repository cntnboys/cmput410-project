import calendar
from datetime import timedelta
import random

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Count
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.core.context_processors import csrf
from django.db.models import Q

import uuid
import Post
import Comment

from main.models import Authors, Friends, Posts, Comments, GithubStreams, TwitterStreams, FacebookStreams
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout

from django.views.decorators.csrf import csrf_exempt

try: import simplejson as json
except ImportError: import json
#import request
#from request.auth import HTTPBasicAuth
#from django.utils import simplejson

#http://stackoverflow.com/questions/645312/what-is-the-quickest-way-to-http-get-in-python
#http://docs.python-requests.org/en/latest/user/authentication/

def getJsonfromothers(request, flag):
    if (flag == "getFriends"):
        r = request.get('http://cs410.cs.ualberta.ca:41081/api/friends', auth=HTTPBasicAuth('user', 'pass'))
        r2 = request.get('http://service/api/friends/{AUTHOR_ID}', auth=HTTPBasicAuth('user', 'pass'))
        h1 = r.json()
        h2 = r2.json()
        #for obj in h1:
        
        return
    if (flag == "getPosts"):
        r = request.get('http://cs410.cs.ualberta.ca:41081/api/posts/public', auth=HTTPBasicAuth('user', 'pass'))
        r2 = request.get('http://service/api/posts', auth=HTTPBasicAuth('user', 'pass'))
        h1 = r.json()
        h2 = r2.json()
        return
    if (flag == "getFriendStatus"):
        r = request.get("")
        r2 = request.get("")
        return
    if (flag == "getFriendRequest"):
        r = request.get("")
        r2 = request.get("")
        return
    if (flag == "getPostsToAuthUser"):
        r = request.get("")
        r2 = request.get("")
        return
    if (flag == "getSinglePost"):
        r = request.get("")
        r2 = request.get("")
        return
    if (flag == "getCommentofPost"):
        r = request.get("")
        r2 = request.get("")
        return
    if (flag == "getAuthors"):
        r = request.get("")
        r2 = request.get("")
        return
    if (flag == "getOneAuthor"):
        r = request.get("")
        r2 = request.get("")
        return

    return
# Index Page function is used to traverse to our introduction page
# if you are not logged in as a user
# If you are logged in as a user, you will be redirected to the
# stream page with posts.
def indexPage(request):
    context = RequestContext(request)
    if request.user.is_authenticated():

        items = []
        if request.method == "GET":
            for x in Posts.objects.all().order_by("date"):
               items.insert(0,x)


        current_user = request.user.get_username()
        author = Authors.objects.get(username=current_user)
        return render(request, "main.html", {'items' : items, 'author': author })
    else:
        return render(request, 'index/intro.html', request.session)

# Redirect Index function just redirects back into the index page
def redirectIndex(request):
    return redirect(indexPage)

def onePost(request,post_uuid):
    items = []
    if request.user.is_authenticated():
        post = Posts.objects.get(post_uuid=post_uuid)
        items.append(post)
     
    return render(request,'authorpost.html',{'items':items})

# Main Page function allows user to go back to the stream of posts
# If author was to access this page without authentication, then
# author will be prompted to Log in first before going to that page.
def mainPage(request, current_user):
    context = RequestContext(request)
    error_msg = "Not Logged In. Please Login Here."

    if request.user.is_authenticated():
        current_user = request.user.get_username()
        author_id = Authors.objects.get(username=current_user)
    
        items = []

        if request.method == "GET":

            # retrieve private posts of friends
            for f in Friends.objects.all():
                if (f.invitee_id==author_id) and not f.status: #TRUE IF FALSE??
                    for x in Posts.objects.filter(author_id=f.inviter_id, privacy="private"):
                       items.insert(0,x)
                if (f.inviter_id==author_id) and not f.status: #TRUE IF FALSE??
                    for x in Posts.objects.filter(author_id=f.invitee_id, privacy="private"):
                       items.insert(0,x)
        
            # retrieve all public posts
            for x in Posts.objects.filter(privacy="public"):
               items.insert(0,x)
        
            # retrieve all private posts of current user (these have been left out in all above queries)
            for x in Posts.objects.filter(author_id=author_id, privacy="private"):
               items.insert(0, x)


            items.sort(key=lambda x: x.date, reverse=True)

	 
            return render(request,'main.html',{'items':items,
                                                'author':author_id })
    
    else:
        return render(request, 'login.html', {'error_msg':error_msg})

# Log in Page function is a check for authenticated author log in
# If author inputs incorrect or non exisiting things in the fields,
# then author will be prompted that either the input was incorrect or
# input does not exist
def loginPage(request):

    if request.method == "POST":

        # Handle if signin not clicked
        if len(request.POST) == 0:
            return render(request, 'login.html')

        username = request.POST.get('username', "").strip()
        password = request.POST.get('password', "").strip()
        error_msg = None

        # Check if fields are filled.
        if username and password:

            user = authenticate(username=username, password=password)
            # Determine if user exists.
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(mainPage, current_user=request.user.get_username())

                    """
                    This is an attempt to get sessions up. HALP.

                    author = Authors.objects.get(username=username, 
                            location='bubble')
                    author_dict = {'authors' : author}



                    response = render_to_response("main.html", author_dict, context)             
                    return response

                    try:        

                        template = loader.get_template('main.html')
                        context = RequestContext(request, request.session)

                        return HttpResponse(template.render(context))

                    
                        data = json.dumps({
                                'author_uuid' : author.__dict__['author_uuid'],
                                'username': username })
                        return HttpResponse(data, content_type='application/json')
                    

                    except (KeyError, Authors.DoesNotExist):

                        request.session['author_uuid'] = None
                        request.session['username'] = None
                        logout(request)

                        error_msg = "Cannot store session information." 
                        return render (request, 'login.html', {'error_msg':error_msg })
                    """


                else:
                    error_msg = """Account is deactivated. Please contact 
                                website hosts for further assistance."""

                    return render (request, 'login.html', {'error_msg':error_msg })

            else:
                error_msg = "Username or password is not valid. Please try again." 
                return render (request, 'login.html', {'error_msg':error_msg })


        else:
            error = "Missing either a username or password. Please supply one "

        error_msg = error_msg if error else "Unknown Error."
        return render(request, 'login.html', {'error_msg': error_msg})

    else:
        return render(request, 'login.html')

# Log out function allows user to log out of the current authenticated account
# and the author will be redirected to the intro page.
def logout(request):
    # Logout function redefined in import statement by Chris Morgan
    # http://stackoverflow.com/questions/7357127/django-logout-crashes-python

    context = RequestContext(request)
    auth_logout(request)
    return redirect(indexPage)

# TODO: use profile template to load page of FOAF
# Function is still a work in progress for part 2
def foaf(request,userid1=None,userid2=None):
	# we want to check if userid1 is friends with/is current user then check if 
	# userid1 is friends with userid2.. if so load userid2's profile so they can be friended?
	current_user = request.user
	user1 = Authors.objects.get(userid=userid1)
	print user1
	print user2
	user2 = Authors.objects.get(userid=userid2)
	inviter = Friends.objects.get(userid1=inviter_id.author_uuid)
	items = []
	# if logged in
	#if request.user.is_authenticated():
		# for e in Friends.objects.filter(invitee_id.author_uuid=user1): 
		# 	if Friends.objects.filter(inviter_id.author_uuid = user2) and e.status = True:
		# 		a = Authors.objects.filter(author_uuid=user2)
		# 		items.append(a)
        	
  #       for e in Friends.objects.filter(inviter_id.author_uuid=user1): 
  #           if Friends.objects.filter(invitee_id.author_uuid=user2) and e.status = True:
  #           	a = Authors.objects.filter(author_uuid=user2)
  #           	items.append(a)
	# foaf.html should be a profile page of userid2 ie: service/author/userid2 when that's working
	return render(request, 'foaf.html',{'items':items})
  
# Friend Request function currently default method is GET which will retrieve
# the friends request the logged in author has.
# If POST method, a check to see if friend request exists, if the friend request exists
# the the status of the friend request changes to True, and if the friend request does not
# exist then we create a friend request from the current author to the selected author.
def friendRequest(request):
    items = []
    ufriends = []
    current_user = request.user
    if request.method == 'GET':
        print current_user.id
        print "in get"
        #print request.user.is_authenticated()

        # if logged in
        if request.user.is_authenticated():
            aUser = Authors.objects.get(username=current_user, location="bubble")
            for e in Friends.objects.filter(invitee_id=aUser):
                if e.status is False :
                    a = Authors.objects.filter(author_uuid=e.inviter_id.author_uuid)
                    items.append(a)

        return render(request, 'friendrequest.html',{'items':items, "author": aUser })

    if request.method == 'POST':
    	userid = current_user.id
        print userid
        print "in post"
        theirUname = request.POST["follow"]
        
        theirAuthor = Authors.objects.get(username=theirUname, location="bubble")
        ourName = Authors.objects.get(username=current_user, location="bubble")
        if request.user.is_authenticated():
            current_user = request.user.username

        #If there exists an entry in our friends table where U1 has already added U2 then flag can be set true now
        if Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False):
            print "here!"
            updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor).update(status=True)
        elif Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor, status=False):
            print "there!"
            updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor).update(status=True)
        else:
            new_invite = Friends.objects.get_or_create(invitee_id = theirAuthor, inviter_id = ourName)

            
                #e = Friends.objects.filter(invitee_id=theirAuthor, inviter_id=ourName, status=False)
                # f = Friends.objects.filter(inviter_id=theirAuthor, invitee_id=ourName, status=False)
            
            
                # if e:
                #    e.update(status=True)
                #if f:
                #   f.update(Status=True)
            
        yourprofileobj = Authors.objects.get(username=current_user, location="bubble")
        items.append(yourprofileobj)
            
            # for e in Friends.objects.filter(invitee_id.author_uuid=current_user.id):
            #   if e.status is False :
            #       a = Authors.objects.filter(author_uuid=e.inviter_id.author_uuid)
            #       ufriends.append(a)
        print items

        return render(request, 'profile.html', {'items' : items, 'ufriends' : ufriends,
                        "author": yourprofileobj} )
    
# Friends function takes in the request for retrieving the friends
# of the author you are logged in as. Default is a GET method retrieving
# all friends of the author. POST method is used when searching a specific
# friends of the current author.
def friends(request):
    items = []
    current_user = request.user
    aUser = Authors.objects.get(username=current_user, location="bubble")
    if request.method == 'GET':
        current_user = request.user
        print current_user.id
        #print request.user.is_authenticated()
        # if logged in
        if request.user.is_authenticated():
            for e in Friends.objects.filter(inviter_id=aUser):
                if e.status is True :
                    a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
                    items.append(a)
                    print a

            for e in Friends.objects.filter(invitee_id=aUser):
                if e.status is True :
                    a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
                    if not (a in items):
                        items.append(a)
                        print a

    if request.method == 'POST':
        current_user = request.user
        searchField = request.POST.get("searchuser","")
        print searchField
        
        if request.user.is_authenticated():
            if searchField != "":
                for e in Friends.objects.filter(inviter_id=aUser):
                    if e.status is True :
                        a = Authors.objects.get(name=searchField)
                        if a not in items:
                            items.append(a)
            #print a.values('name')

    print(items)
    return render(request, 'friends.html',{'items':items, 'author':aUser})

# We are not currently using this function anymore. We have condensed this function
# into get a profile.
def getyourProfile(request, current_user, current_userid):
    items = []
    ufriends=[]
    aUser = Authors.objects.get(username=current_user, location="bubble")
    if request.method == "GET":
        
        if request.user.is_authenticated():
            yourprofileobj = Authors.objects.get(username=current_user, location="bubble") 
            current_user = request.user.username 
            current_userid =yourprofileobj.__dict__["author_uuid"]  

            items.append(yourprofileobj)
            """
            for e in Friends.objects.filter(inviter_id.author_uuid=current_user.id):
                if e.status is True :
                    a = Authors.objects.filter(author_uuid=e.invitee_id.author_uuid)
                    ufriends.append(a)
                        #print a.values('name')

            for e in Friends.objects.filter(invitee_id.author_uuid=current_user.id):
                if e.status is True :
                    a = Authors.objects.filter(author_uuid=e.inviter_id.author_uuid)
                    ufriends.append(a)
        else: #do it anyway for now using ID 1 even if not logged in
            for e in Friends.objects.filter(inviter_id.author_uuid=1):
                if e.status is True:
                    a = Authors.objects.filter(author_uuid=e.invitee_id.author_uuid)
                    ufriends.append(a)
        
            for e in Friends.objects.filter(invitee_id.author_uuid=1):
                if e.status is True :
                    a = Authors.objects.filter(author_uuid=e.inviter_id.author_uuid)
                    ufriends.append(a)


        return render(request,'profile.html',{'items':items},{'ufriends':ufriends})
        """
        return render(request,'profile.html',{'items':items,
                                               'author': yourprofileobj })

# Get a Profile receives request and user object and Id for a selected user
# using the GET method process the author's information is pulled from the database
# as well as the current friends the author has will be taken from the database
# displayed on a profile page with the author's uuid in the url.
def getaProfile(request, theusername, user_id):
    items = []
    ufriends = []
    posts = []
    
    if request.method =="GET":
        author = Authors.objects.get(username=request.user.username)
        user = Authors.objects.get(author_uuid=user_id, location="bubble")
        items.append(user)

        for e in Friends.objects.filter(inviter_id=user):
            if e.status is True :
                a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
                ufriends.append(a)
        #print a.values('name')

        for e in Friends.objects.filter(invitee_id=user):
            if e.status is True :
                a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
                if not (a in items):
                    ufriends.append(a)

        # if current user views their profile, display all own posts
        if user==author:
            for x in Posts.objects.filter(author_id=user):
                posts.insert(0, x)


        else:

            # BETTER than the for loop BUT cannot filter with status=True for some reason!
            #if Friends.objects.filter(inviter_id=author, invitee_id=user, status=True) or Friends.objects.filter(inviter_id=user, invitee_id=author, status=True):
            #   for x in Posts.objects.filter(author_id=user, privacy="private"):
            #       posts.insert(0, x)
            for f in Friends.objects.all():
                if f.invitee_id==author and f.inviter_id==user and not f.status: #TRUE IF FALSE??
                    for x in Posts.objects.filter(author_id=f.inviter_id, privacy="private"):
                        posts.insert(0,x)
                if f.invitee_id==user and f.inviter_id==author and not f.status: #TRUE IF FALSE??
                    for x in Posts.objects.filter(author_id=f.invitee_id, privacy="private"):
                        posts.insert(0,x)

            for x in Posts.objects.filter(author_id=user, privacy="public"):
                posts.insert(0, x)

        posts.sort(key=lambda x: x.date, reverse=True)


        return render(request,'profile.html',{'items':items, 'posts':posts, 'ufriends':ufriends, 'author': user})

    if request.method == "POST":
        user = request.POST["username"]
        print(user)

        yourprofileobj = Authors.objects.get(username=user, location="bubble")
        items.append(yourprofileobj)

        for e in Friends.objects.filter(inviter_id=yourprofileobj):
            if e.status is True :
                a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
                ufriends.append(a)
        #print a.values('name')

        for e in Friends.objects.filter(invitee_id=yourprofileobj):
            if e.status is True :
                a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
                ufriends.append(a)
        print(ufriends)
        return render(request,'profile.html',{'items':items,'ufriends':ufriends, 'author': yourprofileobj})


# EditProfile is a function that we have not implemented yet.
# This function will be implemented in part 2
def editProfile(request, current_user):
    return render(request, 'Editprofile.html')

# Make post function retrieves the title, text, and if image exists, the three fields
# to store into the database adding on the author who created the post.
# After storage of the comment, author is redirected back to the main page
# displaying the most recent post on the main page.
def makePost(request):
    if request.method == "POST":
        
        current_user = request.user.username
        
        author_id = Authors.objects.get(username=current_user)
        title = request.POST["title"]
        author_uuid = Authors.objects.get(username=current_user)

        content = request.POST["posttext"]
        
        privacy = request.POST["privacy"]
        
        #author_uuid = "heyimcameron"
      
        try:
            image=request.FILES["image"]
        except:
            image=""
        
        new_post = Posts.objects.get_or_create(author_id = author_id,
                title = title, content=content, image=image, privacy = privacy )

        return redirect(mainPage, current_user=request.user.username)

# Register Page function is called when author is on the registration page
# All fields on the registration pages are received to store into the database.
# If a username exists then author will be prompted that the user name exists and
# the will have to choose a different username.
# Same for the email if the author inputted a email that already exists,
# then author will be prompted a message saying that email exists and have to use a
# different email.
# If author successfully registers a user, then they will be reidrected to the
# log in page.
def registerPage(request):
    if request.method == 'POST':

        error_msg = None
        success = None

        # Multivalue Dictionary Bug from Post by adamnfish 
        # (http://stackoverflow.com/questions/5895588/
        # django-multivaluedictkeyerror-error-how-do-i-deal-with-it)
        name=request.POST.get("name", "")
        username=request.POST["username"]
        password=request.POST["password"]
        email=request.POST.get("email", "")
        github=request.POST.get("github", "")
        facebook=request.POST.get("facebook", "")
        twitter=request.POST.get("twitter", "")
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
        success = "Registration complete. Please sign in."
        return HttpResponseRedirect("/main/login", {"success": success})

    else:
        
        # Render Register Page
        return render(request, 'Register.html')

# Searching User Page is a function currently unimplemented. This will be a fuction
# that might come in handy for part 2 searching users of another host server.
def searchPage(request):
    items = []
    if request.method == 'POST':
        #searchField = request.POST["searchuser"]
        current_user = request.user
        print current_user.id
        #print request.user.is_authenticated()
        
        # if logged in
        if request.user.is_authenticated():
            for e in Friends.objects.filter(inviter_id=current_user):
                if e.status is True :
                    a = Authors.objects.filter(author_uuid=e.invitee_id.author_uuid)
                    items.append(a)
            #print a.values('name')
            
            for e in Friends.objects.filter(invitee_id=current_user):
                if e.status is True :
                    a = Authors.objects.filter(author_uuid=e.inviter_id.author_uuid)
                    items.append(a)

    return render(request, 'search.html',{'items':items})
      

#getting Json objects to send to other groups 

#needs authentication implemented into functions



def getfriendrequests(request):
    items = []
    if request.method == "GET":
        for x in Freinds.objects.all():
            items.insert(0,x)
    return HttpResponse(json.dumps({'freinds' : items}))


#/main/getfriendstatus/?user=<user1>/<user2>
def getfriendstatus(request):
    items = []
    jsonfriend = {}
  
    if request.method == "GET":
        x = request.GET.get('user', '')
        x = x.split("/")

        user1 = str(x[0])
        user2 = str(x[1])

        print(user1)
        print(user2)

        authors = {}
        authors['query']='friends'
        authors['authors'] = [user1,user2]
        
    
    #now have author uuid

        #    9f9e584fb35e4c859d80d226f44ec150,88d23b032d0a4f46b572bb3e854c49ef
       
        if Authors.objects.filter(author_uuid = user1).count() >=1:
            author1 = Authors.objects.get(author_uuid = user1)
        else:
            authors['friends'] = "NO"
            return HttpResponse(json.dumps(authors,indent=4, sort_keys=True))

        if Authors.objects.filter(author_uuid = user2).count() >=1:
            author2 = Authors.objects.get(author_uuid = user2)
        else:
            authors['friends'] = "NO"
            return HttpResponse(json.dumps(authors,indent=4, sort_keys=True))

        hey = str(author1.author_id)
        hey2 = str(author2.author_id)

        print("hey",hey)
        print("hey2", hey2)

        
        #check if they are friends        
        if Friends.objects.filter(invitee_id=hey2, inviter_id=hey):
            print "here!"
            statusobj = Friends.objects.get(invitee_id = hey2, inviter_id = hey)
        elif Friends.objects.filter(inviter_id=hey2, invitee_id=hey):
            print "there!"
            statusobj = Friends.objects.get(invitee_id = hey, inviter_id = hey2)
        else:
            return

        status = statusobj.status
        print("status",status)

        if status == True:
            authors['friends'] = "YES"
        else:
            authors['friends'] = "NO"

    print("authors",authors)
            
        
    return HttpResponse(json.dumps(authors,indent=4, sort_keys=True))



#title, source(our url), content, author (id), host, displayname(username), urlid, 
#need to implement function to get single posts for url
def getposts(request):
    items = []
   
    if request.method == "GET":
        print "here!"
        postobjs = Posts.objects.all()
        for x in postobjs:
            post = {}
        
            post['title'] = x.title
            post['source'] = ""
            post['origin']= ""
            post['description'] = ""
            post['content-type'] = ""
            post['content'] = x.content
            post['pubdate'] = str(x.date)
            post['guid'] = str(x.post_uuid)

            #need to implement our saving of Privacy ex. "PUBLIC" "PRIVATE" 
            post['visability'] = "PUBLIC"
            
            
            #author
            a = Authors.objects.get(author_uuid = x.author_id.author_uuid)
            author={}
            author['id'] = str(a.author_uuid)
            author['host'] = "thought-bubble.herokuapp.com"
            author['displayname'] = a.username
            author['url'] = "thought-bubble.herokuapp.com/main/" + a.username + "/" + str(a.author_uuid) + "/"
            post['author'] = author
            
            #comments
            post['comments'] = []
            
            items.append(post)

    return HttpResponse(json.dumps({"posts" : items},indent=4, sort_keys=True))
    #return HttpResponse(json.dumps(post))

@csrf_exempt
def newfriendrequest(request):
    items = []
    #print("here")
    if request.method == "POST":
        print("here")
        data = json.loads(request.body)
        authorid = data['author']['id']
        authorhost = data['author']['host']
        friendid = data['friend']['id']
        friendhost = data['friend']['host']
        authorname = data['author']['displayname']
        friendname = data['friend']['displayname']
        friendurl = data['friend']['url']
        location="bubble"

        print("authorid",authorid)
        print("authorhost",authorhost)
        print("authorname",authorname)
        print("friendid",friendid)
        print("friendhost",friendhost)
        print("friendname",friendname)
        email=authorname+"@thought-bubble.com"

        if Authors.objects.filter(username=authorname):
            author1 = Authors.objects.get(username=authorname)
        else:
            author1 = Authors.objects.get_or_create(name=authorname, username=authorname, 
            image="", email=email, github="", 
            facebook="", twitter="", location=authorhost)
        print("author1",author1)

        if Authors.objects.filter(author_uuid = str(friendid)).count() >=1:
            author2 = Authors.objects.get(author_uuid = str(friendid))
            print("author2", author2)
        else:
            print(friendid)

            return HttpResponse('Friend Request Failed: Friend does not exist.')

        author3 = Authors.objects.get(username=authorname)
        print(author3)

        if (Friends.objects.filter(invitee_id = author3, inviter_id=author2, status = False).count() >=1):
            f = Friends.objects.filter(invitee_id = author3, inviter_id=author2).update(status=True)
            return HttpResponse('That user has already requested to be your friend. Accepting their friend request. 200 OK')
        elif (Friends.objects.filter(inviter_id = author3, invitee_id=author2, status = False).count() >=1):
            return HttpResponse('Your previous friend request to that user is still pending approval.')
        elif (Friends.objects.filter(invitee_id = author3, inviter_id=author2, status = True).count() >=1):
            return HttpResponse('You are already friends.')
        elif (Friends.objects.filter(inviter_id = author3, invitee_id=author2, status = True).count() >=1):
            return HttpResponse('You are already friends.')
        else:
            newinvite = Friends.objects.get_or_create(inviter_id = author3, invitee_id=author2)
            print(newinvite)
            return HttpResponse('200 OK')
        return HttpResponse('Friend Request Failed.')

@csrf_exempt
def Foafvis(request):
    items = []
    current_user = request.user
    if request.method == "POST":
        
        data = json.loads(request.body)
        
        postid = data['id']
        
        authorid = data['author']['id']
        host = data['author']['host']
        friend = data['friends']

        print(authorid)
        print(friend)

        print("host",host)

        #check their host 1
        friendslist = []

        for x in friend:
            if Authors.objects.filter(author_uuid = str(x)).count() >=1:
                friendslist.append(x)
                print(friendslist)
                postreq = {}
                postreq['query'] = "friends"
                postreq['author'] = authorid
                postreq['authors'] = friendslist

        #host = "http://127.0.0.1:8000/"
        #print("hi2")
        #print(host+"main/checkfriends/?user="+authorid)
        url = host+"main/checkfriends/?user="+authorid
        r = request.post(url, data=json.dumps(postreq))

        # Response, status etc
        print(r.text)
        print(r.status_code)
        print(str(postid))
        thePost = Posts.objects.get(post_uuid = str(postid))
        #myAuthor = Authors.objects.get(author_uuid = str(lara))
        greg = Authors.objects.get(author_uuid = str(authorid))
        #laraFriends = []
        flag = False
        for friend in Friends.objects.all():
            print(friend.inviter_id.author_uuid)
            #print(myAuthor.author_uuid)
            print(friend.status)
            if (friend.inviter_id.author_uuid == greg.author_uuid and friend.status == True):
                print("in if")
                #laraFriends.append(str(friend.invitee_id.author_uuid))
                flag = True
            elif (friend.invitee_id.author_uuid == greg.author_uuid and friend.status == True):    
                flag = True
                print "in else"
                #laraFriends.append(str(friend.inviter_id.author_uuid))

        posts = Posts.objects.get(post_uuid = postid)
        post = {}

        post['title'] = posts.title
        post['source'] = ""
        post['origin']= ""
        post['description'] = ""
        post['content-type'] = ""
        post['content'] = posts.content
        post['pubdate'] = str(posts.date)
        post['guid'] = str(posts.post_uuid)

        #need to implement our saving of Privacy ex. "PUBLIC" "PRIVATE" 
        post['visability'] = "FOAF"
            
        print("before author")
        #author
        a = Authors.objects.get(author_uuid = posts.author_id.author_uuid)
        author={}
        author['id'] = str(a.author_uuid)
        author['host'] = "thought-bubble.herokuapp.com"
        author['displayname'] = a.username
        author['url'] = "thought-bubble.herokuapp.com/main/" + a.username + "/" + str(a.author_uuid) + "/"
        post['author'] = author
            
        #comments
        post['comments'] = []
            
        items.append(post)
        print(post)
        #jsonfromhost = request.get(host+"main/checkfriends/?user="+authorid)
        #  print(jsonfromhost.ok)
        if (flag == True):
            print("nice")
            #print (json.dumps(post, indent = 4, sort_keys=True))
            return HttpResponse(json.dumps(post, indent = 4, sort_keys=True))


        #return HttpResponse(json.dumps(post))
    return HttpResponse('OK')



  

def getcomments(request):
    items = []
    if request.method == "GET":
        for x in Comments.objects.all():
            items.insert(0,x)
    return HttpResponse(json.dumps({'comments' : items}))

def getgithub(request):
    items = []
    if request.method == "GET":
        for x in GithubStreams.objects.all():
            items.insert(0,x)
    return HttpResponse(json.dumps({'github' : items}))


@csrf_exempt
# /main/checkfriends/?user=<user>
def checkfriends(request):
    #getting info in
    if request.method == "POST":
        x = request.GET.get('user', '')
        data = json.loads(request.body)
        print 'FriendsData: "%s"' % request.body 

        #author = str(data['author'])
        author = str(x)
        print(author)

        authors = data['authors']
        newauthors = []

        author1 = Authors.objects.get(author_uuid = author)
        hey = str(author1.author_id)
        # ef6728777e36445d8d45d9d5125dc4c6 ng1
        # 9e4ac346d9874b7fba14f27b26ae45bb ng3
        #print("authors",authors)
        #print("author1",author1)
        for x in authors:
            newthing = str(x)
            #print("newthing",newthing)
            if Authors.objects.filter(author_uuid=newthing):
                author2 = Authors.objects.get(author_uuid = newthing)
                hey2 = str(author2.author_id)
                #print ("hey2",hey2)
                if Friends.objects.filter(invitee_id=hey2, inviter_id=hey, status = True):
                    newauthors.append(str(x))
                elif Friends.objects.filter(inviter_id=hey2, invitee_id=hey, status = True):
                    #print "there!"
                    newauthors.append(str(x))
                else:
                    return
        myjson = {}
        myjson['query'] = "friends"
        myjson['author'] = author
        myjson['friends'] = newauthors

            

        print("dump",json.dumps(myjson))

        
        

        return HttpResponse(json.dumps(myjson, indent=4, sort_keys=True))

       

    #creating info out

        

        

    



    
