import calendar
from datetime import timedelta
import random
import time
import urllib2

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
        #print "before for"
        for auth in Authors.objects.filter(location = "thought-bubble.herokuapp.com"):
            #print "after for"
            author={}
            author['id'] = str(auth.author_uuid)
            author['host'] = str(auth.location)
            author['displayname'] = str(auth.username)
            author['url'] = str("thought-bubble.herokuapp.com/main/" + auth.username + "/" + str(auth.author_uuid))
            authors.append(author)
            #print authors
            
    return HttpResponse(json.dumps({"authors" : authors}, indent=8, sort_keys=True))


# curl --request GET '127.0.0.1:8000/main/api/getauthorposts/?authorid=293d3415aaa14f779efc7f11ce8e0306/'
# how to figure out authenticated user? request.user=AnonymousUser 
# seems like we need more backend logic to allow for specific people
@logged_in_or_basicauth()
def getPostsByAuthor(request):
    print("start")
    posts = []
    items = []

    if request.method == "GET":        
        current_user = str(request.user.get_username())
        #print("current-user",current_user)
        myid = Authors.objects.get(username=str(current_user))
        #print("start")
        authorid = request.GET.get('authorid', '')
        #print("end")
        #print(authorid)

        try:
            a = Authors.objects.get(author_uuid = str(authorid))
        except:
            response = HttpResponse(content="{message: not authenticated}",content_type="text/HTML; charset=utf-8")
            response.status_code = 404
            response['message'] = 'not authenticated'
            return response



        # public posts by author
        for x in Posts.objects.filter(author_id = a, privacy="public"):
            items.insert(0,x)

        # if current user is friends with author
        for f in Friends.objects.all():
             #print("authorid:",authorid)
             #print("invitee_id",f.invitee_id.author_id)
             if (f.invitee_id.author_id==myid.author_id) and f.status:
                if str(f.invitee_id.username) == a.username:
                    print("same prerson")
                else:
                    for x in Posts.objects.filter(author_id=a, privacy="friends"):
                        #print("1: ",x)
                        #print("f: ",f.invitee_id.username,":",current_user)
                        items.insert(0,x)
                    
            
             if (f.inviter_id.author_id==myid.author_id) and f.status:
                if f.inviter_id.username == a.username:
                    print("same person")
                else:
                    for x in Posts.objects.filter(author_id=a, privacy="friends"):
                        #print("2: ",x)
                        #print("f: ",f.inviter_id.username,":",current_user)
                        items.insert(0,x)
        
        # posts by author marked for us
        for x in Posts.objects.filter(author_id = a ,privacy=str(current_user)):
            #print("for: ",str(current_user), "id :", x.post_id, "x: ", x)
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

            # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            # ''                 foaf ?                               ''
            # ''      privacy = current_user (all posts for me)       ''
            # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            # get posts meant for current user? can privacy be this user? friends?
            # for x in Posts.objects.filter(author_id = a privacy=current_user):
            #     print("for user: ", current_user)

            # maybe not this one
            # for x in Posts.objects.filter(author_id = a privacy = foaf)):
            #     print("by current user"")


    return HttpResponse(json.dumps({"posts" : posts},indent=4, sort_keys=True))


#################################################################################
#                          API Function Calls Are Here                          #
#                          Part 2: Get Others                                          #
#################################################################################


#from django.utils import simplejson

#http://stackoverflow.com/questions/645312/what-is-the-quickest-way-to-http-get-in-python
#http://docs.python-requests.org/en/latest/user/authentication/

def getAuthorsFromOthers():
    
    #curl -u dan:host:password http://cs410.cs.ualberta.ca:41084/api/friends
    url2 = 'http://cs410.cs.ualberta.ca:41084/api/friends'
    string2 = "Basic "+ base64.b64encode('dan:host:password')
    headers2 = {'Authorization':string2, 'Host': 'host'}
    r2 = requests.get(url2, headers=headers2)
    content2 = json.loads(r2.content)
    for author in content2:
        try:
            new_author = Authors.objects.get(author_uuid=author["id"])
        except:
            author_uuid = author["id"]
            name = author["displayname"]
            username = author["displayname"]
            email = username + "@ualberta.ca"
            location = "cs410.cs.ualberta.ca:41084"
        
            new_author = Authors.objects.get_or_create(name=name, username=username, author_uuid=author_uuid, email=email, location=location, github="")[0]

    return None

def formatUuid(id):
    if id.find("-"):
        compare_id = id[:8]+"-"+id[8:12]+"-"+id[12:16]+"-"+id[16:20]+"-"+id[20:]
    else:
        compare_id = id.replace("-", "")
    
    return compare_id

def updateThePosts(content):
    
    print(content)
    for post in content:
    
        author_uuid = post["author"]["id"]
        print author_uuid
        try:
            author = Authors.objects.get(author_uuid=author_uuid)
        except:
      
            try:
                author_uuid = formatUuid(author_uuid)
                author = Authors.objects.get(author_uuid=author_uuid)
            except:
                author_uuid = post["author"]["id"]
                name = post["author"]["displayname"]
                username = post["author"]["displayname"]
                email = username + "@ualberta.ca"
                location = "cs410.cs.ualberta.ca:41084"
                    
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
                        #date = post["pubDate"]
                        #date = time.strptime(date, "YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]")
                title = post["title"]
                        
                new_post = Posts.objects.get_or_create(author_id=author, post_uuid=post_uuid, privacy=privacy, content=content, title=title)[0]#date=date
            
        for comment in post["comments"]:
                
            author_uuid = comment["author"]["id"]
            try:
                comment_author = Authors.objects.get(author_uuid=author_uuid)
            except:
                author_uuid = formatUuid(author_uuid)
                comment_author = Authors.objects.get(author_uuid=author_uuid)
                    
            try:
                new_comment = Comments.objects.get(comment_uuid=comment["guid"])
            except: #comment date?
                comment_uuid = comment["guid"]
                content = comment["comment"]
                        
                new_comment = Comments.objects.get_or_create(comment_uuid=comment_uuid, post_id=new_post, author_id=comment_author)[0]
        
   
    return None


def getOneAuthorPosts(author_id):

    url2 = 'http://cs410.cs.ualberta.ca:41084/api/author/'+str(author_id)+'posts/'
    
    string2 = "Basic "+ base64.b64encode('dan:host:password')
    
    headers2 = {'Authorization':string2, 'Host': 'host'}
    r2 = requests.get(url2, headers=headers2)
    
    try: #if the author actually has posts
        content2 = json.loads(r2.content)
        
        print r2
        updateThePosts(content2)
    
    except:
        pass
    return None


def getPostsFromOthers():
    
    url2 = 'http://cs410.cs.ualberta.ca:41084/api/posts'
    
    string2 = "Basic "+ base64.b64encode('dan:host:password')
    
    headers2 = {'Authorization':string2, 'Host': 'host'}
    r2 = requests.get(url2, headers=headers2)
    
    content2 = json.loads(r2.content)
    
    updateThePosts(content2)
    
    #url = 'http://grepme.github.io/cmput410-project/api/posts'
    #r = requests.get(url)
    #content = json.loads(r.content)
    #updateThePosts(content)
    
    return None


def getFriendsOfAuthors(author_uuid):

    # SAVE THE FRIENDS HERE
    #NOT WORKING PROPERLY GETTING A 400 ERROR FOR BAD  REQUESTS 
    url2 = 'http://cs410.cs.ualberta.ca:41084/api/friends/'
    
    string2 = "Basic "+ base64.b64encode('dan:host:password')
    
    headers2 = {'Authorization':string2, 'Content-Type':'application/json', 'Accept':'*/*'}
    
    author_list2 = []
    
    for author in Authors.objects.all():
        
        author_list2.insert(0,str(author.author_uuid))

    data2 = { "query":"friends","authors":author_list2, "author":str(author_uuid)}
    
    print ("d2: ", data2)
    print ("au: ",author_uuid)
    r2 = requests.post(url2+str(author_uuid), data=json.dumps(data2), headers=headers2)
    
    print ("r2content: " ,r2.content)
    
    content2 = json.loads(r2.content)

    author = Authors.objects.get(author_uuid=author_uuid)

    try:
        for friend_uuid in content2["authors"]:
            author2 = Authors.objects.get(author_uuid=friend_uuid)
            print author.author_uuid
            print author2.author_uuid
            try:
                new_friend=Friends.objects.get(inviter_id=author, invitee_id=author2)
                new_friend.update(status=1)
                print "INVITER ID AUTHOR"
        
            except:
                try:
                    new_friend=Friends.objects.get(inviter_id=author2, invitee_id=author)
                    new_friend.update(status=1)
                    print "INVITER ID AUTHOR222"
                
                except:
                    new_friend = Friends.objects.get_or_create(inviter_id=author, invitee_id=author2, status=0, frequest=1)
                    print "NEW FRIEND!"

    except:
        print "This author is local only!"

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
        author = Authors.objects.get(username=request.user.get_username())
        return render(request, "main.html", {"author":author})

    return render(request, 'index/intro.html')

# Redirect Index function just redirects back into the index page
def redirectIndex(request):
    return redirect(indexPage)

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
                if ( Authors.objects.get(username=username).status == False ):
                    error_msg = "Account Inactive. Please Wait for Web Administrator to Approve This Account "
                    return render (request, 'login.html', {'error_msg':error_msg }) 

                if user.is_active:
                    login(request, user)
                    uuid = Authors.objects.get(username=username).author_uuid
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
    Session.objects.all().delete()
    return redirect(indexPage)

# Main Page function allows user to go back to the stream of posts
# If author was to access this page without authentication, then
# author will be prompted to Log in first before going to that page.
@logged_in_or_basicauth()
def mainPage(request, current_user):
    context = RequestContext(request)
    current_user = request.user.get_username()
    author = Authors.objects.get(username=current_user)

    items = []
    ufriends=[]
    items2 = []

    if request.method == "GET":

#try:
#           if counter % 20 == 0:
#               counter += 1
        getAuthorsFromOthers()
        getPostsFromOthers()

        for author in Authors.objects.all():
            getFriendsOfAuthors(author.author_uuid)


#for author in Authors.objects.all():
            #getOneAuthorPosts(author.author_uuid)

                #Grabs Github Materials
        githubAggregator(current_user)
            #print "endgit"
            #else:
            #   counter+=1
            #except:
            #    print "Errors Here"

        #get friends of user for post input
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
        
        #print("ufreinds",ufriends)
        for x in ufriends:
            print(x.username)

        # retrieve posts of friends
        for f in Friends.objects.all():
            #print("authorid:",author_id.author_id)
            #print("invitee_id",f.invitee_id.author_id)
            if (f.invitee_id.author_id==author.author_id) and f.status:
                for x in Posts.objects.filter(author_id=f.inviter_id.author_id).filter(Q(privacy="friends")|Q(privacy="bubblefriend")):
                    print("gothere2222")
                    items.insert(0,x)
                    
            if (f.inviter_id.author_id==author.author_id) and f.status:
                for x in Posts.objects.filter(author_id=f.invitee_id.author_id).filter(Q(privacy="friends")|Q(privacy="bubblefriend")):
                    items.insert(0,x)


        # retrieve all public posts
        # retrieve all private posts of current user (these have been left out in all above queries)
        # retrieve all private posts of current user (these have been left out in all above queries)
        for x in Posts.objects.filter(Q(privacy="public") | 
            Q(author_id=author.author_id, privacy="private") | Q(privacy=current_user) ):
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

        return render(request,'main.html',{'items':items, 'author':author ,
                                           'ufriends':ufriends})


@logged_in_or_basicauth()
def onePost(request, post_uuid):
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
    # if logged in
    #if request.user.is_authenticated():
        # for e in Friends.objects.filter(invitee_id.author_uuid=user1): 
        #   if Friends.objects.filter(inviter_id.author_uuid = user2) and e.status = True:
        #       a = Authors.objects.filter(author_uuid=user2)
        #       items.append(a)
            
  #       for e in Friends.objects.filter(inviter_id.author_uuid=user1): 
  #           if Friends.objects.filter(invitee_id.author_uuid=user2) and e.status = True:
  #             a = Authors.objects.filter(author_uuid=user2)
  #             items.append(a)
    # foaf.html should be a profile page of userid2 ie: service/author/userid2 when that's working
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
    current_user = request.user
    if request.method == 'GET':
        print current_user.id
        print "in get"
        #print request.user.is_authenticated()

        # if logged in
        if request.user.is_authenticated():
            aUser = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")
            for e in Friends.objects.filter(invitee_id=aUser, frequest=True):
                if e.status is False :
                    a = Authors.objects.filter(author_uuid=e.inviter_id.author_uuid)
                    items.append(a)

        return render(request, 'friendrequest.html',{'items':items, "author": aUser })

    if request.method == 'POST':
        userid = current_user.id
        print userid
        print "in post"
        theirUname = request.POST["follow"]
        try:
            theirAuthor = Authors.objects.get(username=theirUname, location="thought-bubble.herokuapp.com")
            ourName = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")
            for e in Friends.objects.filter(inviter_id=theirAuthor):
	            if e.status is True :
	                a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
	                ufriends.append(a)
        #print a.values('name')

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
                print("here!")
                updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor).update(status=1, invitee_follow =1, frequest=0)
            elif Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor, status=False, frequest=True):
                print("there!")
                updateStatus = Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor).update(status=1, inviter_follow=1, frequest=0)
            elif Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor, status=False, frequest=False):
                print("newthere")
                updateStatus = Friends.objects.filter(inviter_id=ourName, invitee_id=theirAuthor).update(status=0, inviter_follow=1, frequest=1)
            elif Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = False, invitee_follow=False):
                print("theyinv me before, no follow")
                updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = False, invitee_follow=False).delete()
                new_invite = Friends.objects.get_or_create(invitee_id = theirAuthor, inviter_id = ourName, inviter_follow = 1,invitee_follow=0, frequest=1, status =0) # new friend with follow info preserved
            elif Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = True, invitee_follow=True):
                print("theyinv me before, all follow")
            	updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = True, invitee_follow=True).delete()
            	new_invite = Friends.objects.get_or_create(invitee_id = theirAuthor, inviter_id = ourName, inviter_follow = 1,invitee_follow=1, frequest=1, status =0) # new friend with follow info preserved
            elif Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = False, invitee_follow=True):
				print("theyinv me before, I used to follow")
				updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = False, invitee_follow=True).delete()
				new_invite = Friends.objects.get_or_create(invitee_id = theirAuthor, inviter_id = ourName, inviter_follow = 1,invitee_follow=0, frequest=1, status =0) # new friend with follow info preserved
            elif Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = True, invitee_follow=False):
                print("theyinv me before, They followed")
            	updateStatus = Friends.objects.filter(invitee_id=ourName, inviter_id=theirAuthor, status=False, frequest=False, inviter_follow = True, invitee_follow=False).delete()
                new_invite = Friends.objects.get_or_create(invitee_id = theirAuthor, inviter_id = ourName, inviter_follow = 1,invitee_follow=1, frequest=1, status =0) # new friend with follow info preserved
            else:
                print("create try")
                new_invite = Friends.objects.get_or_create(invitee_id = theirAuthor, inviter_id = ourName, inviter_follow = 1, frequest=1, status =0) # new friend request means u auto-follow
                print("ni: ", new_invite)    
		    

            yourprofileobj = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")
            items.append(yourprofileobj)

        
            print("itemsfr:", items)
        
            return render(request, 'profile.html', {'items' : items, 'ufriends' : ufriends, 'friends' : friends,
                      "author": theirAuthor} )

        except:
            print ("not local author")

#second group friend request
# not working because of csrf token problems
        try:
            theirAuthor = Authors.objects.get(username=theirUname, location= "cs410.cs.ualberta.ca:41084")
            print "their author"
            ourName = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")
            print "our author"
            url = "http://cs410.cs.ualberta.ca:41084/api/friendrequest"
            string = "Basic "+ base64.b64encode("dan:host:password")
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
            print theirAuthor.username
            print headers
            print url
            print payload
            r = requests.post(url,data=json.dumps(payload), headers=headers)
            print r

            # SAVE POTENTIAL FRIEND
#new_friend = Friends.get_or_create(inviter_id=ourName, invitee_id = theirAuthor, follow=0, status=0, frequest=1)
            #print r.status_code
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
            print ("not author on this host")

            
        yourprofileobj = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")
        items.append(yourprofileobj)
            
            # for e in Friends.objects.filter(invitee_id.author_uuid=current_user.id):
            #   if e.status is False :
            #       a = Authors.objects.filter(author_uuid=e.inviter_id.author_uuid)
            #       ufriends.append(a)
#       print items

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
            #print a.values('name')

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
    # git_author = Authors.objects.get(author_uuid=user_id)
    
    author = Authors.objects.get(username=current_user)
    authoruuid = Authors.objects.get(author_uuid=user_id).author_uuid
    #authoruuid = Authors.objects.get(username=current_user).author_uuid #gets current user uuid instead of the person clicked on
    
    #try:
    #if author.location != "thought-bubble.herokuapp.com":
    #   getOneAuthorPosts(author.author_uuid)# this is also redundant with get posts
    getFriendsOfAuthors(user_id)

#except:
#       print("Offline")

    if request.method =="GET" or request.method=="POST":
        try:
            user = Authors.objects.get(author_uuid=authoruuid, location="thought-bubble.herokuapp.com")
        except:
#user = Authors.objects.get(author_uuid=user_id, location="bubble")

            user = Authors.objects.get(author_uuid=authoruuid, location="cs410.cs.ualberta.ca:41084")
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

        return render(request,'profile.html',{'items':items, 'posts':posts, 'ufriends':ufriends, 'author': user, 'friends' :friends, 'location': locationflag})

    # if request.method == "POST":
    #     user = request.POST["username"]
    #     print(user)

    #     yourprofileobj = Authors.objects.get(username=user)
    #     items.append(yourprofileobj)

    #     for e in Friends.objects.filter(inviter_id=yourprofileobj):
    #         if e.status is True :
    #             a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
    #             ufriends.append(a)
    #     #print a.values('name')

    #     for e in Friends.objects.filter(invitee_id=yourprofileobj):
    #         if e.status is True :
    #             a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
    #             ufriends.append(a)
    #     print(ufriends)
    #     return render(request,'profile.html',{'items':items,'ufriends':ufriends, 'author': yourprofileobj})


# EditProfile is a function that we have not implemented yet.
# This function will be implemented in part 2
def editProfile(request, current_user):
    if request.method == "POST":
        usernamein=request.POST["username"]
        fullname =request.POST["fullname"]
        emailin = request.POST["email"]
        githubin = request.POST["github"]
        imagein = request.POST["image"]

        #find author object needed to update
        try:
            Authors.objects.filter(username=usernamein).update(name=str(fullname),email=str(emailin),github=githubin,image=imagein)
            error_message = "Profile updated"
            print("Profile updated")
        except:
            print("email already exists")
            error_message = "Email already exists"
            
    return render(request, 'profile.html',{'error_msg': error_message})

#editpost
def editpost(request):
    if request.method == "POST":
        titlein = request.POST["title"]
        imagein = request.POST["image"]
        postidin = request.POST["postid"]
        contentin = request.POST["content"]

        #find post to update

        try:
            Posts.objects.filter(post_id=str(postidin)).update(title=str(titlein),image=imagein,content=str(contentin))
        except:
            pass

    return render(request, 'main.html')
            
                                                    

# Make post function retrieves the title, text, and if image exists, the three fields
# to store into the database adding on the author who created the post.
# After storage of the comment, author is redirected back to the main page
# displaying the most recent post on the main page.
@logged_in_or_basicauth()
def makePost(request):
    if request.method == "POST":
        
        current_user = request.user.username
        
        author_id = Authors.objects.get(username=current_user)
        title = request.POST["title"]
        author_uuid = Authors.objects.get(username=current_user)

        content = request.POST["posttext"]
        
        privacy = str(request.POST["privacy"])
        print("privacy",privacy)
        
        if privacy == current_user:
            privateauthor = str(request.POST["privateauthor"])
            print("privateauthor:",privateauthor)
            if privateauthor != "":
                privacy = privateauthor
                print("privacy2:",privacy)

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
        author_id = Authors.objects.get(username=current_user)
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
@logged_in_or_basicauth()
def getfriendrequests(request):
    items = []
    if request.method == "GET":
        for x in Freinds.objects.all():
            items.insert(0,x)
    return HttpResponse(json.dumps({'freinds' : items}))


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

        print(user1)
        print(user2)

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
@logged_in_or_basicauth()
def getposts(request):
    items = []
    current_user = request.user.get_username()
    blocked = Blocked.objects.all()
    for x in blocked:
        if (x.blockedname == current_user):

            return HttpResponse("You're blocked.")
    if request.method == "GET":
        print "here!"
        postobjs = Posts.objects.all()
        for x in postobjs:
            if x.privacy == "public":
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
                post['visibility'] = "public"
            
            
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

#@logged_in_or_basicauth()

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
        location="thought-bubble.herokuapp.com"

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
            image="", email=email, github="", location=authorhost)
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
            f = Friends.objects.filter(invitee_id = author3, inviter_id=author2).update(status=1)
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
                print ("oj: ",postreq['author'])

        #host = "http://127.0.0.1:8000/"
        #print("postreq: "postreq)
        print(host+"main/checkfriends/?user="+authorid+"/")
        #url = host+"main/checkfriends/?user="+str(authorid)
        #print("url: ", url)
        #r = requests.post(url, data=json.dumps(postreq))
        #r = urllib2.urlopen(str(url), json.dumps(postreq))
        #content = r.read()
        newauthors = []

        print("here")
        # Response, status etc
        #print(r.status_code)
        print(str(authorid))

        try:
            thePost = Posts.objects.get(post_uuid=str(postid))
        except ObjectDoesNotExist:
            return HttpResponse("Bad Post ID")

        print("post: ", thePost )
        #myAuthor = Authors.objects.get(author_uuid = str(lara))
        print("ok",str(data['author']['id']))
        greg = Authors.objects.get(author_uuid = str(data['author']['id']))
        print("greg: ",greg)
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
            return HttpResponse(json.dumps(post, indent = 4, sort_keys=True), )


        #return HttpResponse(json.dumps(post))
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
        author1 = Authors.objects.get(author_uuid = str(x))
        #print("ajsd")
        hey = str(author1.author_id)
        # ef6728777e36445d8d45d9d5125dc4c6 ng1
        # 9e4ac346d9874b7fba14f27b26ae45bb ng3
        #print("author1: ",author1)
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
        
        myjson['query'] = "friends"
        myjson['author'] = author
        myjson['friends'] = newauthors

        #print("dump",json.dumps(myjson))
        return HttpResponse(json.dumps(myjson, indent=4, sort_keys=True),)

def githubAggregator(user):
    entries = []
    author = Authors.objects.get(username = user)
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
        #print("commit", item['title'])
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
        thepost = Posts.objects.get(post_uuid=x)
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

#
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
        author_id = Authors.objects.get(username=str(current_user))
        
         #get freinds of user for post input
        author = Authors.objects.get(username=current_user)
        user = Authors.objects.get(author_uuid=author_id.author_uuid)
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
        current_user = request.user
        if request.method == 'POST':
                userid = current_user.id
                print userid
                print "in unfriend"
                theirUname = request.POST["follow"]
                theirAuthor = Authors.objects.get(username=theirUname, location="thought-bubble.herokuapp.com")
                ourName = Authors.objects.get(username=current_user, location="thought-bubble.herokuapp.com")

				# for e in Friends.objects.filter(inviter_id=ourName):
				# 	if e.status is True :
				# 		a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
				# 		items.append(a)

				# for e in Friends.objects.filter(invitee_id=ourName):
				# 	if e.status is True :
				# 		a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
				# 		if not (a in items):
				# 			items.append(a)
				# 			print a

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

                print("items",items)

                return render(request, 'friends.html',{'items':items, 'author':ourName})
    return None


# TODO: Check on This
@logged_in_or_basicauth()
def unfollow(request):
    if request.user.is_authenticated():
        items = []
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
                        items.append(a)
                        print a

                for e in Friends.objects.filter(inviter_id=ourName):
                    if e.invitee_follow is True :
                        a = Authors.objects.get(author_uuid=e.invitee_id.author_uuid)
                        items.append(a)
                        print a

                print("items",items)

                return render(request, 'follow.html',{'items':items, 'author':ourName})
    return None

@logged_in_or_basicauth()
def follow(request):
    if request.user.is_authenticated():
        items = []
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
                    items.append(a)
            for e in Friends.objects.filter(invitee_id=ourName):
                if e.inviter_follow is True :
                    a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
                    items.append(a)
                    print a
            #items.append(yourprofileobj)

            print("items",items)
            print("ourName: ",ourName.username)

            return render(request, 'follow.html',{'items':items, 'author':ourName})

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
                    items.append(a)
            for e in Friends.objects.filter(invitee_id=ourName):
                if e.inviter_follow is True :
                    a = Authors.objects.get(author_uuid=e.inviter_id.author_uuid)
                    items.append(a)
                    print a


            print("items",items)

            return render(request, 'follow.html',{'items':items, 'author':ourName})


def custom404(request):
    return render(request, 'custom404.html')


