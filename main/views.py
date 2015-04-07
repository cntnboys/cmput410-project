import calendar
from datetime import timedelta
import random
import time
import urllib2
import datetime

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.core.context_processors import csrf

import uuid
import Post
import Comment

from main.models import Authors, Friends, Posts, Comments, GithubPosts, Nodes,Blocked
from getAPI import getAPI
from basicHttpAuth import view_or_basicauth, logged_in_or_basicauth, has_perm_or_basicauth 
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

try: import simplejson as json
except ImportError: import json

import base64
import requests
from requests.auth import HTTPBasicAuth

# Github feed stuff
import feedparser
from django.utils.html import strip_tags

home = "thought-bubble.herokuapp.com"
cs410 = "cs410.cs.ualberta.ca:41084"
projecthub = "projecthub.ca"
counter = 0
#################################################################################
#                          API Function Calls Are Here                          #
#                          Part 1: Get                                          #
#################################################################################
# API call for all authors from our server
@logged_in_or_basicauth()
def getAllAuthors(request):
    authors = []
    if request.method == "GET":
        for auth in Authors.objects.filter(location = home):
            author={}
            author['id'] = str(auth.author_uuid)
            author['host'] = str(auth.location)
            author['displayname'] = str(auth.username)
            author['url'] = str("thought-bubble.herokuapp.com/main/" + auth.username + "/" + str(auth.author_uuid))
            authors.append(author)
            
    return HttpResponse(json.dumps({"authors" : authors}, indent=8, sort_keys=True))


# curl --request GET '127.0.0.1:8000/main/api/getauthorposts/?authorid=293d3415aaa14f779efc7f11ce8e0306/'
# how to figure out authenticated user? request.user=AnonymousUser 
# seems like we need more backend logic to allow for specific people
@logged_in_or_basicauth()
def getPostsByAuthor(request):
    posts = []
    items = []

    if request.method == "GET":        
        current_user = str(request.user.get_username())
        try:
            myid = Authors.objects.get(username=str(current_user))
        except ObjectDoesNotExist:
            response = HttpResponse(content="{message: current user does not exist}",content_type="text/HTML; charset=utf-8")
            response.status_code = 404
            response['message'] = 'current user does not exist'
            return response

        authorid = request.GET.get('authorid', '')

        try:
            a = Authors.objects.get(author_uuid = str(authorid), location=home)
        except ObjectDoesNotExist:
            response = HttpResponse(content="{message: author does not exist}",content_type="text/HTML; charset=utf-8")
            response.status_code = 404
            response['message'] = 'author does not exist'
            return response

        print("after try", a)

        # public posts by author
        try:
            for x in Posts.objects.filter(author_id=a, privacy="public"):
                items.insert(0,x)

        except ObjectDoesNotExist:
            print "No Posts"

        # if current user is friends with author
        for f in Friends.objects.all():
             if (f.invitee_id.author_id==myid.author_id and f.invitee_id.location==home) and f.status:
                if str(f.invitee_id.username) == a.username:
                    continue
                else:
                    for x in Posts.objects.filter(author_id=a, location=home, privacy="friends"):
                        items.insert(0,x)
                    
            
             if (f.inviter_id.author_id==myid.author_id) and f.status:
                if f.inviter_id.username == a.username:
                    continue
                else:
                    for x in Posts.objects.filter(author_id=a, privacy="friends"):
                        items.insert(0,x)
        
        # posts by author marked for us
        for x in Posts.objects.filter(author_id = a ,privacy=str(current_user)):
            items.insert(0,x)

        items.sort(key=lambda x: x.date, reverse=True)

        #comments here
        for x in items:
            post = {}
            post['title'] = str(x.title)
            post['source'] = ""
            post['origin']= ""
            post['description'] = ""
            post['content-type'] = ""
            post['content'] = x.content
            post['pubdate'] = str(x.date)
            post['guid'] = str(x.post_uuid)

        #need to implement our saving of Privacy ex. "PUBLIC" "PRIVATE" 
            print("PRIVACY: ", str(x.privacy))
            post['visibility'] = str(x.privacy)
        
            #author
            author={}
            author['id'] = str(a.author_uuid)
            author['host'] = str(a.location)
            author['displayname'] = str(a.username)
            author['url'] = str("thought-bubble.herokuapp.com/main/" + a.username + "/" + str(a.author_uuid))
            post['author'] = author

            # comments
            comments = []
            for comment in Comments.objects.filter(post_id = x.post_id):
                print("comment: ",comment)
                commAuth = Authors.objects.get(author_uuid = str(x.author_id.author_uuid))
                commAuthJson = {}
                commJson= {}
                theid = str(commAuth.author_uuid)
                location = commAuth.location
                theuser = commAuth.username
                thecontent = comment.content
                thedate = comment.date
                thecommuuid = str(comment.comment_uuid)
                commAuthJson['id'] = str(theid)
                commAuthJson['host'] = str(location)
                commAuthJson['displayname'] = str(theuser)
                commJson['comment'] = str(thecontent)
                commJson['pubDate'] = str(thedate)
                commJson['guid'] = str(thecommuuid)
                commJson['author'] = commAuthJson
                comments.append(commJson)
       
                post['comments'] = comments

            posts.append(post)


        return HttpResponse(json.dumps({"posts" : posts},indent=4, sort_keys=True))


#################################################################################
#                          API Function Calls Are Here                          #
#                          Part 2: Get Others                                   #
#################################################################################


#from django.utils import simplejson

#http://stackoverflow.com/questions/645312/what-is-the-quickest-way-to-http-get-in-python
#http://docs.python-requests.org/en/latest/user/authentication/

def getAuthorsFromOthers(location):
    #curl -u dan:host:password http://cs410.cs.ualberta.ca:41084/api/friends
    
    if location==cs410:
        url = 'http://cs410.cs.ualberta.ca:41084/api/friends'
        string = "Basic "+ base64.b64encode('uuid:host:password')
        headers = {'Authorization':string, 'Host': 'host'}

    elif location==projecthub:
        url = 'http://projecthub.ca/api/authors'
        headers = {}

    r = requests.get(url, headers=headers)
    content = json.loads(r.content)

    if location==projecthub:
        for author in content["authors"]:
            try:
                new_author = Authors.objects.get(author_uuid=author["id"])
            except:
                author_uuid = author["id"]
                name = author["displayname"]
                username = author["displayname"]
                email = username + "@ualberta.ca"
                
                host = author["host"]
                if "thought-bubble" in host:
                    host = home
                if "project" in host:
                    host = location;
            
                new_author = Authors.objects.get_or_create(name=name, username=username, author_uuid=author_uuid, email=email, location=host, github="")[0]

    if location==cs410:
        for author in content:
            try:
                new_author = Authors.objects.get(author_uuid=author["id"])
            except:
                author_uuid = author["id"]
                name = author["displayname"]
                username = author["displayname"]
                email = username + "@ualberta.ca"
            
                host = author["host"]

                if "thought-bubble" in host:
                    host = home
                if "cs410" in host:
                    host = location
                if host=="host":
                    host=location
                
                new_author = Authors.objects.get_or_create(name=name, username=username, author_uuid=author_uuid, email=email, location=host, github="")[0]

    return None

def updateThePosts(content, location):

    try:
        posts = content["posts"]
    except:
        posts=content

    for post in posts:

        try:
            Posts.objects.get(post_uuid=str(post["guid"]))
            continue;
        except ObjectDoesNotExist:
            print "Time to Create Post"

        author_uuid = post["author"]["id"]

        try:
            author = Authors.objects.get(author_uuid=author_uuid)
        except:
            try:
                author = Authors.objects.get(author_uuid=author_uuid)
            except:
                author_uuid = post["author"]["id"]
                name = post["author"]["displayname"]
                username = post["author"]["displayname"]
                email = username + "@ualberta.ca"

                author = Authors.objects.get_or_create(name=name, username=username, author_uuid=author_uuid, email=email, location=location, github="")[0]
            
        try:
            new_post = Posts.objects.get(post_uuid=post["guid"])
        except:
                
            try:
                post_uuid = post["guid"]
                new_post = Posts.objects.get(post_uuid=post_uuid)
            except:
                post_uuid = post["guid"]
                privacy = post["visibility"].lower()
                content = post["description"]
                title = post["title"]
                date = post["pubDate"]
                new_post = Posts.objects.get_or_create(author_id=author, post_uuid=post_uuid, privacy=privacy, content=content, title=title)[0]#date=date
            
        for comment in post["comments"]:          
            author_uuid = comment["author"]["id"]
            try:
                comment_author = Authors.objects.get(author_uuid=author_uuid)
            except:
                comment_author = Authors.objects.get(author_uuid=author_uuid)
                    
            try:
                new_comment = Comments.objects.get(comment_uuid=comment["guid"])
            except: #comment date?
                comment_uuid = comment["guid"]
                content = comment["comment"]
                new_comment = Comments.objects.get_or_create(comment_uuid=comment_uuid, post_id=new_post, author_id=comment_author)[0]
    return None

#MAY NOT DO!!!
def getOneAuthorPosts(author_id):
    url2 = 'http://cs410.cs.ualberta.ca:41084/api/author/'+str(author_id)+'posts/'
    string2 = "Basic "+ base64.b64encode('uuid:host:password')
    headers2 = {'Authorization':string2, 'Host': 'host'}
    r2 = requests.get(url2, headers=headers2)
    
    try: #if the author actually has posts
        content2 = json.loads(r2.content)
        
        updateThePosts(content2)
    
    except:
        pass
    return None


def getPostsFromOthers(location):
    
    if location==cs410:
        url = 'http://cs410.cs.ualberta.ca:41084/api/posts'
        string = "Basic "+ base64.b64encode('uuid:host:password')
        headers = {'Authorization':string, 'Host': 'host'}
    
    elif location==projecthub:
        url = 'http://projecthub.ca/api/posts'
        headers = {}

    r = requests.get(url, headers=headers)
    content = json.loads(r.content)

    updateThePosts(content, location)

    return None


def getFriendsOfAuthors(author_uuid, location):
    if location==cs410:
        url = 'http://cs410.cs.ualberta.ca:41084/api/friends/'
        string = "Basic "+ base64.b64encode('uuid:host:password')
        headers = {'Authorization':string, 'Content-Type':'application/json', 'Accept':'*/*'}
        
    if location==projecthub:
        url = 'http://projecthub.ca/api/friends/'
        headers = {'Content-Type':'application/json', 'Accept':'*/*'}

    author_list = []
    
    for author in Authors.objects.all():
        
        author_list.insert(0,str(author.author_uuid))

    data = { "query":"friends","authors":author_list, "author":str(author_uuid)}

    r = requests.post(url+str(author_uuid), data=json.dumps(data), headers=headers)
    
    content = json.loads(r.content)

    author = Authors.objects.get(author_uuid=author_uuid)

    try:
        for friend_uuid in content["authors"]:
            author2 = Authors.objects.get(author_uuid=friend_uuid)
            print author.author_uuid
            print author2.author_uuid
            try:
                new_friend=Friends.objects.get(inviter_id=author, invitee_id=author2)
                new_friend.update(status=1)

            except:
                try:
                    new_friend=Friends.objects.get(inviter_id=author2, invitee_id=author)
                    new_friend.update(status=1)
                
                
                except:
                    new_friend = Friends.objects.get_or_create(inviter_id=author, invitee_id=author2, status=1, frequest=1)

    except:
        print "This author is local only!"

    return None

def makeFriendRequest(theirUName,ourUName, locations):
    if locations == cs410:
        theirAuthor = Authors.objects.get(username=theirUName, location=locations)
        ourName = Authors.objects.get(username=ourUName, location="thought-bubble.herokuapp.com")
        url = "http://cs410.cs.ualberta.ca:41084/api/friendrequest"
        string = "Basic "+ base64.b64encode("uuid:host:password")
        headers = {"Authorization":string, "Host":"host", "Content-Type":"application/json"}
        oid = str(ourName.author_uuid)
        odname = str(ourName.username)
        furl ="http://cs410.cs.ualberta.ca:41084/author/%s" % str(theirAuthor.author_uuid)
        fdname = str(theirAuthor.username)
        fid = str(theirAuthor.author_uuid)
        payload =  {    "query": "friendrequest",
                        "author":{
                            "id":oid,
                            "host":"http://thought-bubble.herokuapp.com/",
                            "displayname":odname
                        },
                        "friend": {
                            "id":fid,
                            "host":"http://cs410.cs.ualberta.ca:41084/",
                            "displayname":fdname,
                            "url":furl
                        }
                    }
        r = requests.post(url,data=json.dumps(payload), headers=headers)

    return None


#################################################################################
#                            Django Pages                                       #
#                                                                               #
#################################################################################
# Index Page function directs to our introduction page
# if you are not logged in as a user
def indexPage(request):
    context = RequestContext(request)

    # Makes sure pages get author information when logged in when
    # navigating to main.
    if request.user.is_authenticated():
        author = Authors.objects.get(username=request.user.get_username(), location=home)
        return render(request, "main.html", {"author":author})

    return render(request, 'index/intro.html')

# Redirect Index function just redirects back into the index page
def redirectIndex(request):
    return redirect(indexPage)

# Log in Page function is a check for authenticated author log in
# If author inputs incorrect or non existing things in the fields,
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
                if ( Authors.objects.get(username=username, location=home).status == False ):
                    error_msg = "Account Inactive. Please Wait for Web Administrator to Approve This Account "
                    return render (request, 'login.html', {'error_msg':error_msg }) 

                if user.is_active:
                    login(request, user)
                    uuid = Authors.objects.get(username=username, location=home).author_uuid
                    request.session['username']= username
                    request.session['uuid']= uuid
                    response = redirect(mainPage, current_user=request.user.get_username())
                    return response

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
    auth_logout(request)
    #Session.objects.all().delete()
    return redirect(indexPage)

# Main Page function allows user to go back to the stream of posts
# If author was to access this page without authentication, then
# author will be prompted to Log in first before going to that page.
@logged_in_or_basicauth()
def mainPage(request, current_user):
    context = RequestContext(request)
    current_user = request.user.get_username()
    author = Authors.objects.get(username=current_user, location=home)

    items = []
    ufriends=[]
    items2 = []

    if request.method == "GET":
        # Try Except Chain for Offline Capabilities
        try:
           getAuthorsFromOthers(cs410)
        except:
           print "Cannot Get Authors from Others"
        try:
             getAuthorsFromOthers(projecthub)
        except:
            print "Cannot Get Authors from projecthub"

        try:
            getPostsFromOthers(cs410)
        except:
            print "Cannot Get Posts Others"
        try:
            getPostsFromOthers(projecthub)
        except:
            print "Cannot Get Posts from projecthub"
        
        try:
            getFriendsOfAuthors(author.author_uuid, cs410)
        except:
            "Current user has no friends on cs410"
        try:
            getFriendsOfAuthors(author.author_uuid, projecthub)
        except:
            "Current user has no friends on projecthub"

        try:
            print "GitHub Start"
            githubAggregator(current_user)
        except:
            print "Cannot Get Github"

        items2.append(author)

        for e in Friends.objects.filter(inviter_id=author):
            if e.status is True :
                a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
                ufriends.append(a)
  
        for e in Friends.objects.filter(invitee_id=author):
            if e.status is True :
                a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
                if not (a in items):
                    ufriends.append(a)

        # retrieve posts of friends
        for f in Friends.objects.all():
            if (f.invitee_id.author_id==author.author_id) and f.status:
                for x in Posts.objects.filter(author_id=f.inviter_id.author_id).filter(Q(privacy="friends")|Q(privacy="bubblefriend")):
                    items.insert(0,x)
                    
            if (f.inviter_id.author_id==author.author_id) and f.status:
                for x in Posts.objects.filter(author_id=f.invitee_id.author_id).filter(Q(privacy="friends")|Q(privacy="bubblefriend")):
                    items.insert(0,x)

        # retrieve all public posts
        # retrieve all private posts of current user (these have been left out in all above queries)
        # retrieve all private posts of current user (these have been left out in all above queries)
        for x in Posts.objects.filter(Q(privacy="public") | Q(author_id=author.author_id, privacy="private") | Q(privacy=current_user) ):
           items.insert(0,x)

        for post in items:
            comments = []
            try:
                for c in Comments.objects.all():
                    if (c.post_id==post):
                        comments.insert(0,c)
                post.comments = comments
                items.sort(key=lambda x: x.date, reverse=True)
            except:
                post.comments = None

        # This got overwritten some how?
        author = Authors.objects.get(username=current_user, location=home)

        return render(request,'main.html',{'items':items, 'author':author ,
                                           'ufriends':ufriends, 'items2': items2})

@logged_in_or_basicauth()
def onePost(request,author_name, post_uuid):
    items = []
    post = Posts.objects.get(post_uuid=post_uuid)
    items.append(post)
     
    return render(request,'authorpost.html',{'items':items})


# TODO: use profile template to load page of FOAF
# Function is still a work in progress for part 2
@logged_in_or_basicauth()
def foaf(request, userid1, userid2):
    # we want to check if userid1 is friends with/is current user then check if 
    # userid1 is friends with userid2.. if so load userid2's profile so they can be friended?
    current_user = request.user
    user1 = Authors.objects.get(userid=userid1)
    print user1
    print user2
    user2 = Authors.objects.get(userid=userid2)
    inviter = Friends.objects.get(userid1=inviter_id.author_uuid)
    items = []
    return render(request, 'foaf.html',{'items':items})
  
# Friend Request function currently default method is GET which will retrieve
# the friends request the logged in author has.
# If POST method, a check to see if friend request exists, if the friend request exists
# the the status of the friend request changes to True, and if the friend request does not
# exist then we create a friend request from the current author to the selected author.
@logged_in_or_basicauth()
def friendRequest(request):
    items = []
    ufriends = []
    friends = []
    follow = []

    current_user = request.user
    if request.method == 'GET':
        # if logged in
        if request.user.is_authenticated():
            aUser = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")
            for e in Friends.objects.filter(invitee_id=aUser, frequest=True):
                if e.status is False :
                    a = Authors.objects.filter(author_uuid=e.inviter_id.author_uuid)
                    items.append(a)

            for e in Friends.objects.filter(invitee_id=aUser):
                if e.inviter_follow is True :
                    a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
                    follow.append(a)

            for e in Friends.objects.filter(inviter_id=aUser):
                if e.invitee_follow is True :
                    a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
                    follow.append(a)

        return render(request, 'friendrequest.html',{'items':items, "author": aUser,"follow":follow })

    if request.method == 'POST':
        userid = current_user.id
        theirUname = request.POST["follow"]
        theirUuid = request.POST["followuuid"]
        try:
            theirAuthor = Authors.objects.get(username=theirUname, author_uuid=theirUuid)
            ourName = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")
            for e in Friends.objects.filter(inviter_id=theirAuthor):
	            if e.status is True :
	                a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
	                ufriends.append(a)

		    for e in Friends.objects.filter(invitee_id=theirAuthor):
		        if e.status is True :
		            a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
		            if not (a in items):
		                ufriends.append(a)

	        # Loading Friend/follow logic
			for e in Friends.objects.filter(inviter_id=theirAuthor):
				if(str(e.invitee_id.username) == str(current_user)):
					friends.append(e)

			for e in Friends.objects.filter(invitee_id=theirAuthor):
				if(str(e.inviter_id.username) == str(current_user)):
					friends.append(e)


            if request.user.is_authenticated():
                current_user = request.user.username

            #If there exists an entry in our friends table where U1 has already added U2 then flag can be set true now
            if Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=True):
                updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor).update(status=1, invitee_follow =1, frequest=0)
            elif Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor, status=False, frequest=True):
                updateStatus = Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor).update(status=1, inviter_follow=1, frequest=0)
            elif Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor, status=False, frequest=False):
                updateStatus = Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor).update(status=0, inviter_follow=1, frequest=1)
            elif Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = False, invitee_follow=False):
                updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = False, invitee_follow=False).delete()
                new_invite = Friends.objects.get_or_create(invitee_id = theirAuthor, inviter_id = ourName, inviter_follow = 1,invitee_follow=0, frequest=1, status =0) # new friend with follow info preserved
            elif Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = True, invitee_follow=True):
            	updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = True, invitee_follow=True).delete()
            	new_invite = Friends.objects.get_or_create(invitee_id = theirAuthor, inviter_id = ourName, inviter_follow = 1,invitee_follow=1, frequest=1, status =0) # new friend with follow info preserved
            elif Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = False, invitee_follow=True):
				updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = False, invitee_follow=True).delete()
				new_invite = Friends.objects.get_or_create(invitee_id = theirAuthor, inviter_id = ourName, inviter_follow = 1,invitee_follow=0, frequest=1, status =0) # new friend with follow info preserved
            elif Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = True, invitee_follow=False):
            	updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = True, invitee_follow=False).delete()
                new_invite = Friends.objects.get_or_create(invitee_id = theirAuthor, inviter_id = ourName, inviter_follow = 1,invitee_follow=1, frequest=1, status =0) # new friend with follow info preserved
            else:
                new_invite = Friends.objects.get_or_create(invitee_id = theirAuthor, inviter_id = ourName, inviter_follow = 1, frequest=1, status =0) # new friend request means u auto-follow
		    
            yourprofileobj = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")
            items.append(yourprofileobj)

            for e in Friends.objects.filter(inviter_id=ourName):
                if e.status is True :
                    a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
                    items.append(a)

            for e in Friends.objects.filter(invitee_id=ourName):
                if e.status is True :
                    a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
                    if not (a in items):
                        items.append(a)
            #print("itemsfr:", items)
        
            return render(request, 'friends.html', {'items' : items, "author": ourName} )

        except:
            print ("not local author")
            aUser = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")
            for e in Friends.objects.filter(invitee_id=aUser, frequest=True):
                if e.status is False :
                    a = Authors.objects.filter(author_uuid=e.inviter_id.author_uuid)
                    items.append(a)

            for e in Friends.objects.filter(invitee_id=aUser):
                if e.inviter_follow is True :
                    a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
                    follow.append(a)

            for e in Friends.objects.filter(inviter_id=aUser):
                if e.invitee_follow is True :
                    a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
                    follow.append(a)

            return render(request, 'friendrequest.html',{'items':items, "author": aUser, 'follow':follow })

#second group friend request
# not working because of csrf token problems
        try:
            makeFriendRequest(theirUname,current_user, cs410)

            # SAVE POTENTIAL FRIEND
            if request.user.is_authenticated():
                current_user = request.user.username
            if Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=True):
                print "here!"
                updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor).update(status=1, invitee_follow=1, frequest=0)
            elif Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor, status=False, frequest=True):
                print "there!"
                updateStatus = Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor).update(status=1, inviter_follow=1, frequest=0)
            else:
                new_invite = Friends.objects.get_or_create(invitee_id = theirAuthor, inviter_id = ourName, inviter_follow = 1, frequest=1)

            yourprofileobj = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")
            items.append(yourprofileobj)
            print items
            print "items on top"
                
            return render(request, 'profile.html', {'items' : items, 'ufriends' : ufriends,
                              "author": yourprofileobj} )

        except:
            print ("Not author on CMPUT410 host")

            
        yourprofileobj = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")
        items.append(yourprofileobj)

        return render(request, 'profile.html', {'items' : items, 'ufriends' : ufriends, "author": yourprofileobj} )
    
# Friends function takes in the request for retrieving the friends
# of the author you are logged in as. Default is a GET method retrieving
# all friends of the author. POST method is used when searching a specific
# friends of the current author.
def friends(request):
    items = []
    current_user = request.user
    aUser = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")
    if request.method == 'GET':
        current_user = request.user
        
        # if logged in
        if request.user.is_authenticated():
            for e in Friends.objects.filter(inviter_id=aUser):
                if e.status is True :
                    a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
                    items.append(a)

            for e in Friends.objects.filter(invitee_id=aUser):
                if e.status is True :
                    a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
                    if not (a in items):
                        items.append(a)

    if request.method == 'POST':
        current_user = request.user
        searchField = request.POST.get("searchuser","")
        print("SF: ",searchField)
        
        if request.user.is_authenticated():
            if searchField != "":
                for e in Friends.objects.filter(inviter_id=aUser):
                    if e.status is True :
                        a = Authors.objects.get(username=str(searchField))
                        if a not in items:
                            items.append(a)
                for e in Friends.objects.filter(invitee_id=aUser):
                    if e.status is True :
                        a = Authors.objects.get(username=str(searchField))
                        if a not in items:
                            items.append(a)

    print(items)
    return render(request, 'friends.html',{'items':items, 'author':aUser})

# Get a Profile receives request and user object and Id for a selected user
# using the GET method process the author's information is pulled from the database
# as well as the current friends the author has will be taken from the database
# displayed on a profile page with the author's uuid in the url.
@logged_in_or_basicauth()
def getaProfile(request, theusername, user_id):
    items = []
    ufriends = []
    posts = []
    current_user = request.user
    friends = []
    locationflag = 1
    
    author = Authors.objects.get(username=current_user, location=home)

    try:
        view_author = Authors.objects.get(author_uuid=user_id)
        authoruuid = view_author.author_uuid
    except:
        print("Weird Login")    

    try:
        if view_author.location==cs410 or view_author.location==projecthub:
            getFriendsOfAuthors(user_id, view_author.location)
    except:
        print("Offline")

    if request.method =="GET" or request.method=="POST":
        # Only duplication errors should be of users of our local host
        try:
            user = Authors.objects.get(author_uuid=authoruuid)
        except:
            user = Authors.objects.get(author_uuid=authoruuid, location=home)

        items.append(user)

        # Loading Friend/follow logic
        for e in Friends.objects.filter(inviter_id=user):
            #print("inviter=: ", e.inviter_id.username)
            #print("inviter : ",str(e.inviter_id.username), " : ", str(current_user))
            if(str(e.invitee_id.username) == str(current_user)):
            	friends.append(e)

        for e in Friends.objects.filter(invitee_id=user):
            #print("inviter=: ", e.inviter_id.username)
            #print("inviter : ",str(e.inviter_id.username), " : ", str(current_user))
            if(str(e.inviter_id.username) == str(current_user)):
            	friends.append(e)

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
            if Friends.objects.filter(inviter_id=author, invitee_id=user, status=True) or Friends.objects.filter(inviter_id=user, invitee_id=author, status=True):
                for x in Posts.objects.filter(author_id=user, privacy="private"):
                   posts.insert(0, x)

            for x in Posts.objects.filter(author_id=user, privacy="public"):
                posts.insert(0, x)

        posts.sort(key=lambda x: x.date, reverse=True)

        if(len(friends)==0):
        	friends.append(0)

        print("LOCATION: ", str(user.location))
        loca = str(user.location)
        if(loca != "thought-bubble.herokuapp.com"):
			locationflag = 0
			print("f0loc0: ", locationflag)

        print("Friends: ", friends)

        return render(request,'profile.html',{'items':items, 'posts':posts, 'ufriends':ufriends, 
            'author': author, 'viewinguser':user, 'friends' :friends, 'location': locationflag})

# EditProfile is a function that we have not implemented yet.
# This function will be implemented in part 2
def editProfile(request):
    print "Got Author"
    current_user = request.user.username
    

    if request.method == "POST":
        usernamein=request.POST["username"]
        fullname =request.POST["fullname"]
        emailin = request.POST["email"]
        githubin = request.POST["github"]
        imagein = request.FILES["image"]

        #find author object needed to update
        try:
            author = Authors.objects.filter(username=current_user, location=home)
            if imagein == "":
                author.update(name=fullname,email=emailin,github=githubin, status=True)
            else:
                author.update(name=fullname,email=emailin, github=githubin,image=imagein, status=True)
            error_message = "Profile updated"
            print("Profile updated")
        except:
            print("email already exists")
            error_message = "Email already exists"
    
    author = Authors.objects.get(username=current_user, location=home)

    return redirect(getaProfile, theusername=author.username, user_id=author.author_uuid)

# Edit Post
def editpost(request):
    if request.method == "POST":
        titlein = request.POST["title"]
        postidin = request.POST["postid"]
        contentin = request.POST["content"]

        try:
            post = Posts.objects.filter(post_id=str(postidin))

            post.update(title=str(titlein),content=str(contentin))

        except:
            return redirect(mainPage, current_user=request.user.username)

    return redirect(mainPage, current_user=request.user.username)
            
                                                    

# Make post function retrieves the title, text, and if image exists, the three fields
# to store into the database adding on the author who created the post.
# After storage of the comment, author is redirected back to the main page
# displaying the most recent post on the main page.
@logged_in_or_basicauth()
def makePost(request):
    if request.method == "POST":
        
        current_user = request.user.username        
        author_id = Authors.objects.get(username=current_user, location=home)

        title = request.POST["title"]
        content = request.POST["posttext"]
        privacy = str(request.POST["privacy"])
        #print("privacy",privacy)
        
        if privacy == current_user:
            privateauthor = str(request.POST["privateauthor"])
            #print("privateauthor:",privateauthor)
            if privateauthor != "":
                privacy = privateauthor
                #print("privacy2:",privacy)
        try:
            image=request.FILES["image"]
        except:
            image=""
        
        new_post = Posts.objects.get_or_create(author_id = author_id,
                title = title, content=content, image=image, privacy = privacy )

        return redirect(mainPage, current_user=request.user.username)

@logged_in_or_basicauth()
def makeComment(request):
    if request.method == "POST":  
        current_user = request.user.username
        author_id = Authors.objects.get(username=current_user, location=home)
        current_post = request.POST["postid"]
        post_id = Posts.objects.get(post_id=current_post)
        comment = request.POST["comment"]
        
        try:
            image = request.FILES["image"]
        except:
            image=""
    
        new_comment = Comments.objects.get_or_create(author_id = author_id, post_id = post_id, content = comment, image=image)
    
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
        location="thought-bubble.herokuapp.com"

        try:
            image=request.FILES["image"]
        except:
            image=""

        if Authors.objects.filter(username=username):
            error_msg = "Username already exists"
            return render (request, 'Register.html', {'error_msg':error_msg, 'name':name, 'username':username, 
                            'email':email, 'image':image, 'github':github})

        if Authors.objects.filter(email=email):
            error_msg = "Email already exists"
            return render (request, 'Register.html', {'error_msg':error_msg, 'name':name, 'username':username, 
                            'email':email, 'github':github})
           
        new_user = User.objects.create_user(username, email, password)
        new_author = Authors.objects.get_or_create(name=name, username=username, 
            image=image, location=location, email=email, github=github)

        # Successful. Redirect to Login
        success = "Registration complete. Please sign in."

        messages.add_message(request, messages.INFO, success)
        return HttpResponseRedirect("/main/login")

    else:
        # Render Register Page
        return render(request, 'Register.html')

# Searching User Page is a function currently unimplemented. This will be a fuction
# that might come in handy for part 2 searching users of another host server.
@logged_in_or_basicauth()
def searchPage(request):
    items = []
    if request.method == 'POST':
        current_user = request.user
        print current_user.id
        
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
      

#/main/getfriendstatus/?user=<user1>/<user2>
@logged_in_or_basicauth()
def getfriendstatus(request):
    items = []
    jsonfriend = {}
  
    if request.method == "GET":
        x = request.GET.get('user', '')
        x = x.split("/")

        user1 = str(x[0])
        user2 = str(x[1])

        authors = {}
        authors['query']='friends'
        authors['authors'] = [user1,user2]
        
    
    #now have author uuid

        #9f9e584fb35e4c859d80d226f44ec150,88d23b032d0a4f46b572bb3e854c49ef
       
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
@logged_in_or_basicauth()
def getposts(request):
    items = []
    current_user = request.user.get_username()
    try:
        author_id = Authors.objects.get(username=str(current_user))
    except ObjectDoesNotExist:
        return HttpResponse('{"message": "Current user not found"}')

    try:
        blocked = Blocked.objects.all()
        for x in blocked:
            if (x.author_obj == author_id):
                return HttpResponse("You're blocked.")
    except:
        print("checking blocked failed")

    if request.method == "GET":
        postobjs = Posts.objects.all()
        for x in postobjs:
            if x.privacy == "public" and x.author_id.location == "thought-bubble.herokuapp.com":
                post = {}
                post['title'] = x.title
                post['source'] = ""
                post['origin']= ""
                post['description'] = ""
                post['content-type'] = ""
                post['content'] = x.content
                post['pubdate'] = str(x.date)
                post['guid'] = str(x.post_uuid)
               #print("x: ",x)

            #need to implement our saving of Privacy ex. "PUBLIC" "PRIVATE" 
                post['visibility'] = "public"
            
            
            #author

                a = Authors.objects.get(author_uuid = x.author_id.author_uuid)
                author={}
                author['id'] = str(a.author_uuid)
                author['host'] = "thought-bubble.herokuapp.com"
                author['displayname'] = a.username
                author['url'] = "thought-bubble.herokuapp.com/main/" + a.username + "/" + str(a.author_uuid) + "/"
                post['author'] = author

                try:    
                    comments = Comments.objects.filter(post_id = x)
                    commentList = []
                    for n in comments:

                        if(str(a.location) == "thought-bubble.herokuapp.com"):
                            print("n.author_id: ", n.author_id.author_id)
                            commAuth = Authors.objects.get(author_id = n.author_id.author_id)
                            commAuthJson = {}
                            commJson= {}
                            theid = str(commAuth.author_uuid)
                            location = str(commAuth.location)
                            theuser = str(commAuth.username)
                            thecontent = str(n.content)
                            if(thecontent == 'None'):
                                thecontent=""
                            thedate = str(n.date)
                            thecommuuid = str(n.comment_uuid)
                            commAuthJson['id'] = str(theid)
                            commAuthJson['host'] = str(location)
                            commAuthJson['displayname'] = str(theuser)
                            commJson['comment'] = str(thecontent)
                            commJson['pubDate'] = str(thedate)
                            commJson['guid'] = str(thecommuuid)
                            commJson['author'] = commAuthJson
                            commentList.append(commJson)
                except ObjectDoesNotExist:
                    print "no comments to send"
                post['comments'] = str(commentList)
                items.append(post)


    return HttpResponse(json.dumps({"posts" : items}, indent=4, sort_keys=True))

#@logged_in_or_basicauth()
@csrf_exempt
def newfriendrequest(request):
    items = []
    if request.method == "POST":
        data = json.loads(request.body)
        authorid = data['author']['id']
        authorhost = data['author']['host']
        friendid = data['friend']['id']
        friendhost = data['friend']['host']
        authorname = data['author']['displayname']
        friendname = data['friend']['displayname']
        friendurl = data['friend']['url']
        location="thought-bubble.herokuapp.com"

        #print("authorid",authorid)
        #print("authorhost",authorhost)
        #print("authorname",authorname)
        #print("friendid",friendid)
        #print("friendhost",friendhost)
        #print("friendname",friendname)
        email=authorname+"@thought-bubble.com"

        if Authors.objects.filter(username=authorname, author_uuid=authorid):
            author1 = Authors.objects.get(username=authorname, author_uuid=authorid)
        else:
            author1 = Authors.objects.get_or_create(name=authorname, username=authorname, author_uuid=authorid, 
            image="", email=email, github="", location=authorhost)
        print("author1",author1)

        if Authors.objects.filter(author_uuid = str(friendid)).count() >=1:
            author2 = Authors.objects.get(author_uuid = str(friendid))
            print("author2", author2)
        else:
            print(friendid)

            return HttpResponse('Friend Request Failed: Friend does not exist.')
        try:
        	author3 = Authors.objects.get(username=authorname, author_uuid=authorid)
        except ObjectDoesNotExist:
            return HttpResponse('{"message": "Author not found"}')
        print(author3)

        if (Friends.objects.filter(invitee_id = author3, inviter_id=author2, frequest = False).count() >=1):
            f = Friends.objects.filter(invitee_id = author3, inviter_id=author2).update(status=1)
            return HttpResponse('That user has already requested to be your friend. Accepting their friend request. 200 OK')
        elif (Friends.objects.filter(inviter_id = author3, invitee_id=author2, frequest=1).count() >=1):
            return HttpResponse('Your previous friend request to that user is still pending approval.')
        elif (Friends.objects.filter(invitee_id = author3, inviter_id=author2, status = True).count() >=1):
            return HttpResponse('You are already friends.')
        elif (Friends.objects.filter(inviter_id = author3, invitee_id=author2, status = True).count() >=1):
            return HttpResponse('You are already friends.')
        else:
            newinvite = Friends.objects.get_or_create(inviter_id = author3, invitee_id=author2, frequest=1)
            #print(newinvite)
            return HttpResponse('200 OK')
        return HttpResponse('Friend Request Failed.')

#@logged_in_or_basicauth()
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
        friendslist = []

        for x in friend:
            if Authors.objects.filter(author_uuid = str(x)).count() >=1:
                friendslist.append(x)
                print(friendslist)
                postreq = {}
                postreq['query'] = "friends"
                postreq['author'] = authorid
                postreq['authors'] = friendslist

        newauthors = []

        try:
            thePost = Posts.objects.get(post_uuid=str(postid))
        except ObjectDoesNotExist:
            return HttpResponse("Bad Post ID")

        greg = Authors.objects.get(author_uuid = str(data['author']['id']))
        flag = False

        for f in friend:

            try:
                friendauthor = Authors.objects.get(author_uuid=str(f))
                if(Friends.objects.filter(invitee_id=friendauthor, inviter_id=greg)):
                    flag = True
                elif(Friends.objects.filter(inviter_id=friendauthor, invitee_id=greg)):
                    flag = True
            except:
                continue

        posts = Posts.objects.get(post_uuid = str(postid))
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
        post['visibility'] = "FOAF"
            
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
        if (flag == True):
            return HttpResponse(json.dumps(post, indent = 4, sort_keys=True), )
        elif(flag == False):
            return HttpResponse("{ message: NOT FOAF }")

    return HttpResponse('OK')


#@logged_in_or_basicauth()
@csrf_exempt
# /main/api/checkfriends/?user=<user>
def checkfriends(request):
    myjson = {}
    newauthors = []

    #getting info in
    if request.method == "POST":
        x = request.GET.get('user', '')
        data = json.loads(request.body)
        print 'FriendsData: "%s"' % request.body 

        #author = str(data['author'])
        author = str(x)
        #print(author)
        authors = data['authors']
        #print("authors",authors)
        try:
        	author1 = Authors.objects.get(author_uuid = str(x))
        except ObjectDoesNotExist:
            return HttpResponse('{"message": "Queried author not found"}')

        hey = str(author1.author_id)
        for x in authors:
            newthing = str(x)
            #print("newthing",newthing)
            # Need to try except finding the author. Otherwise Ignore it.
            try: 
                if Authors.objects.filter(author_uuid=newthing):
                    author2 = Authors.objects.get(author_uuid = newthing)
                    hey2 = str(author2.author_id)
                    #print ("hey2",hey2)
                    if Friends.objects.filter(invitee_id=hey2, inviter_id=hey, status = True):
                        if str(x) not in newauthors:
                            newauthors.append(str(x))
                    elif Friends.objects.filter(inviter_id=hey2, invitee_id=hey, status = True):
                        #print "there!"
                        if str(x) not in newauthors:
                            newauthors.append(str(x))
                    else:
                        continue
            except:
                continue
        
        myjson['query'] = "friends"
        myjson['author'] = author
        myjson['friends'] = newauthors

        #print("dump",json.dumps(myjson))
        return HttpResponse(json.dumps(myjson, indent=4, sort_keys=True),)

def githubAggregator(user):
    entries = []
    gitname = ""
    author = Authors.objects.get(username = user)

    if author.github == "" or author.github == None:
        return None
    else:
        gitname = author.github

    giturl = "http://www.github.com/"+gitname+".atom"
    #print("giturl",giturl)
    feed = feedparser.parse(giturl)

    for item in feed.entries:
        title = item.title
        #print("title", item['title'],"\n")

        #print("url", item['link'])
        gitname = item['author']
        #print("author", gitname)
        #print("commit", itezm['title'])
        date = item['updated']
        #print("updated", date)
        itemid = item['id']
        #print("ITEMID:",item['id'])

        a = strip_tags(item['summary'])
        content = a.split(gitname)

        if len(content) > 1:
            try:
                content = content[1]
            except IndexError:
                print("content error")
        else:
            content = a

        content = content.replace('\n','')
        #print("content", content)
        #print("desc", desc,"\n")
        privacy = "public" # Public github data

        if(GithubPosts.objects.filter(date = date, gh_uuid = itemid).count() >= 1):
            print("post already exists")
            continue
        else:
            #print("new post")
            if(Posts.objects.filter(author_id = author, title = title, content=content, privacy = privacy,image="" ).count() < 1):
                print("adding")
                new_post = Posts.objects.get_or_create(author_id = author, title = title, content=content, privacy = privacy,date =date,image=""  )
                thepost = Posts.objects.get(author_id = author, title = title, content=content, privacy = privacy,image=""  )
                gh_post = GithubPosts.objects.get_or_create(gh_uuid = itemid, post_id = thepost, date = date, content= content)
            else:
                print("duplicate post content (itemid and date arent the same but post is)")


    #threading.Timer(180, githubAggregator(user)).start() # call function ever 5 mins? this infinite loops atm
    return None

@logged_in_or_basicauth()
def singlepost(request):
    items = []
    if request.method == "GET":
        x = request.GET.get('postid', '')
        print(x)

        try:
        	thepost = Posts.objects.get(post_uuid=x)
        except ObjectDoesNotExist:
            return HttpResponse('{"message": "No such post."}')
        if thepost.privacy == "public":
            post = {}
        
            post['title'] = thepost.title
            
            post['origin']= ""
            post['description'] = ""
            post['content-type'] = ""
            post['content'] = thepost.content
            post['pubdate'] = str(thepost.date)
            post['guid'] = str(thepost.post_uuid)
            print("content: ", thepost.content)

            post['visibility'] = "public"
            print(thepost.author_id.author_uuid)
            
            #author
            a = Authors.objects.get(author_uuid = thepost.author_id.author_uuid)
            author={}
            author['id'] = str(a.author_uuid)
            author['host'] = "thought-bubble.herokuapp.com"
            author['displayname'] = a.username
            author['url'] = "thought-bubble.herokuapp.com/main/" + a.username + "/" + str(a.author_uuid) + "/"
            post['author'] = author
            post['source'] = "http://thought-bubble.herokuapp.com/main/getapost/?="+x+"/"
            post['origin'] = a.location
            
            comments = []
            for n in Comments.objects.filter(author_id = a, post_id = thepost.post_id):
                commAuth = Authors.objects.get(author_uuid = str(n.author_id.author_uuid))
                commAuthJson = {}
                commJson= {}
                theid = str(commAuth.author_uuid)
                location = commAuth.location
                theuser = commAuth.username
                thecontent = n.content
                thedate = n.date
                thecommuuid = str(n.comment_uuid)
                commAuthJson['id'] = str(theid)
                commAuthJson['host'] = str(location)
                commAuthJson['displayname'] = str(theuser)
                commJson['comment'] = str(thecontent)
                commJson['pubDate'] = str(thedate)
                commJson['guid'] = str(thecommuuid)
                commJson['author'] = commAuthJson
                comments.append(commJson)

            #print(comments)
            post['comments'] = str(comments)
                
            items.append(post)

    return HttpResponse(json.dumps({"posts" : items}, indent=4, sort_keys=True),)

@logged_in_or_basicauth()
def authorposts(request):
    print "hello"
    items = []
    ufriends=[]
    items2 = []
    items3 = []

    if request.method == "GET":
        print("yo")
        current_user = str(request.user.get_username())
        print("yo2")
        print("current-user",current_user)
        try:
            author_id = Authors.objects.get(username=str(current_user))
        except ObjectDoesNotExist:
            return HttpResponse('{"message": "Queried author not found"}')


         #get freinds of user for post input
        try:    
            author = Authors.objects.get(username=current_user)
        except ObjectDoesNotExist:
            return HttpResponse('{"message": "Queried author not found"}')
        try:
            user = Authors.objects.get(author_uuid=author_id.author_uuid)
        except ObjectDoesNotExist:
            return HttpResponse('{"message": "Queried user not found"}')

        items2.append(user)

        for e in Friends.objects.filter(inviter_id=user):
            if e.status is True :
                a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
                ufriends.append(a)
  

        for e in Friends.objects.filter(invitee_id=user):
            if e.status is True :
                a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
                if not (a in items):
                    ufriends.append(a)
        
        print("ufreinds",ufriends)
        for x in ufriends:
            print(x.username)

        # retrieve posts of friends
        for f in Friends.objects.all():
             print("authorid:",author_id.author_id)
             print("invitee_id",f.invitee_id.author_id)
             if (f.invitee_id.author_id==author_id.author_id) and f.status:
                 for x in Posts.objects.filter(author_id=f.inviter_id.author_id, privacy="friends"):
                     print("gothere2222")
                     items.insert(0,x)
                    
            
             if (f.inviter_id.author_id==author_id.author_id) and f.status:
                 print("got here11")
                 for x in Posts.objects.filter(author_id=f.invitee_id.author_id, privacy="friends"):
                    items.insert(0,x)
                   
       
    
        # retrieve all public posts
        for x in Posts.objects.filter(privacy="public"):
           items.insert(0,x)

        # retrieve all posts from bubble and that are friends aswell (bubblefreind)
        for f in Friends.objects.all():
            if (f.invitee_id.author_id==author_id.author_id) and f.status:
                for x in Posts.objects.filter(author_id=f.inviter_id.author_id, privacy="bubblefriend"):
                   items.insert(0,x)
            if (f.inviter_id.author_id==author_id.author_id) and f.status:
                for x in Posts.objects.filter(author_id=f.invitee_id.author_id, privacy="bubblefriend"):
                   items.insert(0,x)
    
        # retrieve all private posts of current user (these have been left out in all above queries)
        for x in Posts.objects.filter(author_id=author_id.author_id, privacy="private"):
           items.insert(0, x)

        # retreive all private posts of the current user (sent by another author to us privately :))))) )
        for x in Posts.objects.filter(privacy=current_user):
            items.insert(0,x)

        items.sort(key=lambda x: x.date, reverse=True)

        for post in items:
            comments = []
            try:
                for c in Comments.objects.all():
                    if (c.post_id==post):
                        comments.insert(0,c)
                post.comments = comments
                items.sort(key=lambda x: x.date, reverse=True)
            except:
                post.comments = None

        for x in items:      
            post = {}
            post['title'] = str(x.title)
            post['source'] = ""
            post['origin']= ""
            post['description'] = ""
            post['content-type'] = ""
            post['content'] = x.content
            post['pubdate'] = str(x.date)
            post['guid'] = str(x.post_uuid)

        #need to implement our saving of Privacy ex. "PUBLIC" "PRIVATE" 
            post['visibility'] = str(x.privacy)
          
        #author
            a = Authors.objects.get(author_uuid = x.author_id.author_uuid)
            author={}
            author['id'] = str(a.author_uuid)
            author['host'] = "thought-bubble.herokuapp.com"
            author['displayname'] = str(a.username)
            author['url'] = "thought-bubble.herokuapp.com/main/" + a.username + "/" + str(a.author_uuid) + "/"
            post['author'] = author
        
        #comments
            comments = []
            comments2 = []
            try:
                for c in Comments.objects.all():
                    if (c.post_id==x):
                        comments.insert(0,c)
                c.comments = comments
                items.sort(key=lambda x: x.date, reverse=True)
            except:
                x.comments = None
      
        #for the comments
            for comment in comments:
                commAuth = Authors.objects.get(author_uuid = str(x.author_id.author_uuid))
                commAuthJson = {}
                commJson= {}
                theid = str(commAuth.author_uuid)
                location = commAuth.location
                theuser = commAuth.username
                thecontent = comment.content
                thedate = comment.date
                thecommuuid = str(comment.comment_uuid)
                commAuthJson['id'] = str(theid)
                commAuthJson['host'] = str(location)
                commAuthJson['displayname'] = str(theuser)
                commJson['comment'] = str(thecontent)
                commJson['pubDate'] = str(thedate)
                commJson['guid'] = str(thecommuuid)
                commJson['author'] = commAuthJson
                comments2.append(commJson)
       

            post['comments'] = comments2
            
            items3.append(post)
            
            
    print(items3)       
    #return HttpResponse("OK")
    return HttpResponse(json.dumps({"posts" : items3},indent=4, sort_keys=True))


# This is the function call to delete the post
@logged_in_or_basicauth()
def deletePost(request):
    current_user = request.user.get_username()
    author = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")
    if request.method == 'POST':
        current_post = request.POST["id"]
        try:
            Posts.objects.get(post_id = str(current_post)).delete()
            #print("Post deleted")  
        except ObjectDoesNotExist:
            #print("Post does not exist")
            return redirect(mainPage, current_user=author.username)

    return redirect(mainPage, current_user=author.username)

@logged_in_or_basicauth()
def unfriend(request):
    if request.user.is_authenticated():
        items = []
        follow = []
        current_user = request.user
        if request.method == 'POST':
                userid = current_user.id
                print userid
                print "in unfriend"
                # check on two things to make it less likely to error
                theirUname = request.POST["follow"]
                theirUuid = request.POST["followuuid"]
                theirAuthor = Authors.objects.get(username=theirUname, author_uuid=str(theirUuid)) # location might not be thought-bubble only anymore
                ourName = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")

                #If there exists an entry in our friends table where U1 has already added U2 then flag can be set true now
                if Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=True):
                    print "here!"
                    updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor).update(status=0)
                elif Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor, status=True):
                    print "there!"
                    updateStatus = Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor).update(status=0)


                for e in Friends.objects.filter(inviter_id=ourName):
                    if e.status is True :
                        a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
                        items.append(a)
                        print a

                for e in Friends.objects.filter(invitee_id=ourName):
                    if e.status is True :
                        a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
                        if not (a in items):
                            items.append(a)
                # #items.append(yourprofileobj)

                #print("items",items)

                return render(request, 'friends.html',{'items':items, 'author':ourName, 'follow':follow})
    return None


# TODO: Check on This
@logged_in_or_basicauth()
def unfollow(request):
    if request.user.is_authenticated():
        items = []
        friends = []
        follow = []
        current_user = request.user
        if request.method == 'POST':
                userid = current_user.id
                print("in unfollow")
                theirUname = request.POST["follow"]
                theirAuthor = Authors.objects.get(username=theirUname, location="thought-bubble.herokuapp.com")
                ourName = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")

                #If there exists an entry in our friends table where U1 has already added U2 then flag can be set true now
                if Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor, inviter_follow=True):
                    print("unfollow: IM INVITER; INVFOLLOW=True")
                    updateStatus = Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor).update(inviter_follow=0)
                elif Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, invitee_follow=True):
                    print("unfollow: IM INVITEE; INVFOLLOW=True")
                    updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor).update(invitee_follow=0)


                #If there exists an entry in our friends table where U1 has already added U2 then flag can be set true now
                for e in Friends.objects.filter(invitee_id=ourName):
                    if e.inviter_follow is True :
                        a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
                        follow.append(a)
                        print a

                for e in Friends.objects.filter(invitee_id=ourName):
                    if e.frequest is True :
                        a = Authors.objects.filter(author_uuid=e.inviter_id.author_uuid)
                        items.append(a)
                for e in Friends.objects.filter(inviter_id=ourName):
                    if e.frequest is True :
                        a = Authors.objects.filter(author_uuid=e.invitee_id.author_uuid)
                        items.append(a)

                print("items",items)

                return render(request, 'friendrequest.html',{'items':items, 'author':ourName, 'follow':follow})
    return None

@logged_in_or_basicauth()
def follow(request):
    if request.user.is_authenticated():
        items = []
        friends = []
        follow = []
        current_user = request.user
        if request.method =='GET':
            userid = current_user.id
            #print("in follow")]
            ourName = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")

            # IF they follow YOU then you are never the inviter
            for e in Friends.objects.filter(inviter_id=ourName):
                print("e: ",e)
                if e.invitee_follow is True :
                    a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
                    follow.append(a)
            for e in Friends.objects.filter(invitee_id=ourName):
                if e.inviter_follow is True :
                    a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
                    follow.append(a)
                    print a
            for e in Friends.objects.filter(invitee_id=ourName):
                if e.frequest is True :
                    a = Authors.objects.filter(author_uuid=e.inviter_id.author_uuid)
                    items.append(a)

            #items.append(yourprofileobj)

            print("items",items)
            print("ourName: ",ourName.username)

            return render(request, 'friendrequest.html',{'items':items, 'author':ourName, 'follow':follow})

        if request.method == 'POST':
            userid = current_user.id
            #print("in follow")
            theirUname = request.POST["follow"]
            theirAuthor = Authors.objects.get(username=theirUname, location="thought-bubble.herokuapp.com")
            ourName = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")

            #If there exists an entry in our friends table where U1 has already added U2 then flag can be set true now
            if Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor, inviter_follow=False):
                print("IM INVITER; INVFOLLOW=False")
                updateStatus = Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor).update(inviter_follow=1)
            elif Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, invitee_follow=False):
                print("IM INVITEE; INVFOLLOW=False")
                updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor).update(invitee_follow=1)
            else:
                new_invite = Friends.objects.get_or_create(invitee_id = theirAuthor, inviter_id = ourName, inviter_follow = 1)

            for e in Friends.objects.filter(inviter_id=ourName):
                print("e: ",e)
                if e.invitee_follow is True :
                    a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
                    follow.append(a)
            for e in Friends.objects.filter(invitee_id=ourName):
                if e.inviter_follow is True :
                    a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
                    follow.append(a)
                    print a

            for e in Friends.objects.filter(invitee_id=ourName):
                if e.frequest is True :
                    a = Authors.objects.filter(author_uuid=e.inviter_id.author_uuid)
                    items.append(a)


            print("items",items)

            return render(request, 'friendrequest.html',{'items':items, 'author':ourName, 'follow':follow})


def custom404(request):
    return render(request, 'custom404.html')


