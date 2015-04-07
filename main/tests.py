import calendar
from datetime import datetime
import random

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Count
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.core.context_processors import csrf

from django.db import IntegrityError
from django.db import transaction

from django.utils import timezone
import uuid


from django.test import TestCase

from main.models import Authors, Friends, Posts, Comments, GithubPosts, Nodes

# AUHTOR TESTS
class AuthorTests(TestCase):
    
    # CREATE TWO AUTHORS
    def test_create_author(self):
        
        self.assertEqual(Authors.objects.all().count(), 0)
        
        name = "Ana Marcu"
        username = "aname"
        email = "marcu@ualberta.ca"
        location = "thought-bubble.com"
        image="/path/to/image.jpg"
        github="MyGithub"
        
        author1 = Authors.objects.get_or_create(name=name, username=username,location=location, email=email, image=image, github=github)[0]
        
        # check author exists
        self.assertEqual(Authors.objects.filter(username="aname", location="thought-bubble.com")[0], author1)
        self.assertEqual(Authors.objects.all().count(), 1)
        
        name = "Bob Murley"
        username = "bobmurley"
        email = "murley@ualberta.ca"
        location = "thought-bubble.com"
        
        author2 = Authors.objects.get_or_create(name=name, username=username,location=location, email=email)[0]
        
        # check second author exists
        self.assertEqual(Authors.objects.filter(username="bobmurley", location="thought-bubble.com")[0], author2)
        self.assertEqual(Authors.objects.all().count(), 2)
    
    
    
    # APPROVE AN AUTHOR (admin changes author status in system)
    def test_approve_author(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="aname",location="thought-bubble.com", email="marcu@ualberta.ca")[0]
    
        self.assertEqual(Authors.objects.all().count(), 1)
    
        # retrieve the author, update the status, and save
        author = Authors.objects.get(username = "aname")
        author.status = True
        author.save()
    
        # check that record is updated
        self.assertEqual(Authors.objects.filter(username="aname", location="thought-bubble.com")[0], author)
        #check that previous record does not exist
        self.assertFalse(Authors.objects.filter(username="aname", status=False))
        self.assertEqual(Authors.objects.all().count(), 1)


    # CREATE AN AUTHOR WITH AN EXISTING USERNAME AND EXISTING LOCATION
    def test_create_same_username_location_author(self):
        
        author = Authors.objects.get_or_create(name="Bob Murley", username="bobmurley",location="thought-bubble.com", email="murley@ualberta.ca")[0]
        
        self.assertEqual(Authors.objects.all().count(), 1)
        
        name = "Bob John Murley"
        username = "bobmurley"
        email = "bob@ualberta.ca"
        location = "thought-bubble.com"
        
        # try to create author with existing username and location (unique together)
        try:
            author2 = Authors.objects.get_or_create(name=name, username=username, email=email, location=location)[0]
        except:
            author2 = "Username location not unique together"
        
        # check author not created
        self.assertEqual(author2, "Username location not unique together")
        self.assertEqual(Authors.objects.all().count(), 1)


    # UPDATE AN AUTHOR'S USERNAME
    def test_update_author(self):
        
        author1 = Authors.objects.get_or_create(name="Ana Marcu", username="aname",location="thought-bubble.com", email="marcu@ualberta.ca")[0]
        
        self.assertEqual(Authors.objects.filter(username="aname")[0], author1)
        self.assertEqual(Authors.objects.all().count(), 1)
        
        # retrieve the author, update the username, and save
        author = Authors.objects.get(username = "aname")
        author.username = "anamarcu"
        author.save()
        
        # check that record is updated
        self.assertEqual(Authors.objects.filter(username="anamarcu")[0], author)
        #check that previous record does not exist
        self.assertFalse(Authors.objects.filter(username="aname"))
        self.assertEqual(Authors.objects.all().count(), 1)
    
    # DELETE AN AUTHOR
    def test_delete_author(self):
        
        author = Authors.objects.get_or_create(name="Bob Murley", username="bobmurley",location="thought-bubble.com", email="murley@ualberta.ca")[0]
        
        self.assertEqual(Authors.objects.all().count(), 1)
        
        # retrieve an existing author and delete
        Authors.objects.get(username = "bobmurley").delete()
        
        try:
            deleted = Authors.objects.get(username = "bobmurley")
        except:
            deleted = None
        
        # check the author does not exist
        self.assertEqual(deleted, None)
        self.assertEqual(Authors.objects.all().count(), 0)



# NODES TESTS
class NodesTests(TestCase):
    
    # CREATE A SYSTEM NODE
    def test_create_node(self):

        self.assertEqual(Authors.objects.all().count(), 0)

        node_url = "http://thought-bubble.com"
        node_name = "Thought Bubble"
        
        node = Nodes.objects.get_or_create(node_url=node_url, node_name=node_name)[0]

        # check node exists
        self.assertEqual(Nodes.objects.filter(node_url="http://thought-bubble.com", node_name="Thought Bubble")[0], node)
        self.assertEqual(Nodes.objects.all().count(), 1)

    # CREATE A NODE WITH AN EXISITNG URL
    def test_create_node_same_url(self):

        node1 = Nodes.objects.get_or_create(node_url="http://thought-bubble.com", node_name="Thought Bubble")[0]

        self.assertEqual(Nodes.objects.all().count(), 1)

        node_url = "http://thought-bubble.com"
        node_name = "Second Thought Bubble"

        # try to create a node with an existing url
        try:
            node2 = Nodes.objects.get_or_create(node_url=node_url, node_name=Node_name)[0]
        except:
            node2 = "Url must be unique"

        # check node not created
        self.assertEqual(node2, "Url must be unique")
        self.assertEqual(Nodes.objects.all().count(), 1)


    # UPDATE A SYSTEM NODE
    def test_update_node(self):

        node = Nodes.objects.get_or_create(node_url="http://thought-bubble.com", node_name="Thought Bubble")[0]

        self.assertEqual(Nodes.objects.filter(node_url="http://thought-bubble.com", node_name="Thought Bubble")[0], node)
        self.assertEqual(Nodes.objects.all().count(), 1)

        # retrieve the node, update the name, and save
        node = Nodes.objects.get(node_url="http://thought-bubble.com")
        node.node_name = "Your Thought Bubble"
        node.save()

        # check that record is updated
        self.assertEqual(Nodes.objects.filter(node_url="http://thought-bubble.com")[0], node)
        #check that previous record does not exist
        self.assertFalse(Nodes.objects.filter(node_url="http://thought-bubble.com", node_name="Thought Bubble"))
        self.assertEqual(Nodes.objects.all().count(), 1)


    # DELETE A SYSTEM NODE
    def test_delete_author(self):
    
        node = Nodes.objects.get_or_create(node_url="http://thought-bubble.com", node_name="Thought Bubble")[0]
    
        self.assertEqual(Nodes.objects.all().count(), 1)
    
        # retrieve an existing node and delete
        Nodes.objects.get(node_url="http://thought-bubble.com").delete()
    
        try:
            deleted = Nodes.objects.get(node_url="http://thought-bubble.com", node_name="Thought Bubble")
        except:
            deleted = None
    
        # check the node does not exist
        self.assertEqual(deleted, None)
        self.assertEqual(Nodes.objects.all().count(), 0)


# POSTS TESTS
class PostsTests(TestCase):
    
    # CREATE TWO POSTS FOR AN AUTHOR
    def test_create_post(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="thought-bubble.com", email="marcu@ualberta.ca")[0]
        
        self.assertEqual(Posts.objects.all().count(), 0)
        
        title = "First Post"
        content = "the first post"
        privacy = "public"
        
        # create a post for an author
        post1 = Posts.objects.get_or_create(author_id=author, title=title, content=content, privacy=privacy, image="/path/to/image.jpg")[0]
        
        # check that the post exists
        self.assertEqual(Posts.objects.filter(author_id=author, title="First Post", privacy="public")[0], post1)
        self.assertEqual(Posts.objects.all().count(), 1)
        
        title = "Second Post"
        content = "the second post"
        privacy = "private"
        
        # create another post for the same author
        post2 = Posts.objects.get_or_create(author_id=author, title=title, content=content, privacy=privacy)[0]
        
        # check that the second post exists
        self.assertEqual(Posts.objects.filter(author_id=author, title="Second Post", privacy="private")[0], post2)
        self.assertEqual(Posts.objects.all().count(), 2)
    
    
    # CREATE A POST WITHOUR REFERENCING THE AUTHOR
    def test_create_post_without_author(self):
        
        self.assertEqual(Posts.objects.all().count(), 0)
        
        title = "Third Post"
        content = "the third post"
        privacy = "public"
        
        # try to create post without author
        try:
            post = Posts.objects.get_or_create(title=title, content=content, privacy=privacy)[0]
        except:
            post = "No author"
        
        # check post not created
        self.assertEqual(post, "No author")
        self.assertFalse(Posts.objects.filter(title="Third Post", privacy="public"))
        self.assertEqual(Posts.objects.all().count(), 0)
    
    # UPDATE A POST'S CONTENT TEXT
    def test_update_post(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="local", email="marcu@ualberta.ca")[0]
        post1 = Posts.objects.get_or_create(author_id=author, title="First Post", content="the first post", privacy="public")[0]
        
        self.assertEqual(Posts.objects.filter(author_id=author, content="the first post", privacy="public")[0], post1)
        self.assertEqual(Posts.objects.all().count(), 1)
        
        # retrieve an existing post, update the content, and save
        post = Posts.objects.get(author_id=author, title="First Post", privacy="public")
        post.content = "writing post"
        post.privacy = "private"
        post.save()
        
        # check that record is updated
        self.assertEqual(Posts.objects.filter(author_id=author, content="writing post", privacy="private")[0], post)
        # check that previous record does not exist
        self.assertFalse(Posts.objects.filter(author_id=author, content="the first post", privacy="public"))
        self.assertEqual(Posts.objects.all().count(), 1)
    
    # DELETE A POST
    def test_delete_post(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="thought-bubble.com", email="marcu@ualberta.ca")[0]
        post = Posts.objects.get_or_create(author_id=author, title="First Post", content="the first post", privacy="public")[0]
        
        self.assertEqual(Posts.objects.all().count(), 1)
        
        # retrieve an existing post and delete
        Posts.objects.get(author_id=author, content="the first post", privacy="public").delete()
        
        try:
            deleted = Posts.objects.get(author_id=author, content="the first post", privacy="public")
        except:
            deleted = "deleted"
        
        # check the post does not exist
        self.assertEqual(deleted, "deleted")
        self.assertEqual(Posts.objects.all().count(), 0)


# GITHUB POSTS TESTS
class GithubPostsTests(TestCase):
    
    # CREATE A GITHUB POST RECORD FOR AN EXISTING POST
    def test_create_githubpost(self):

        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="thought-bubble.com", email="marcu@ualberta.ca", github="marcugit")[0]
        
        post = Posts.objects.get_or_create(author_id=author, title="First Post", content="the first post", privacy="public")[0]
    
        gh_uuid = uuid.uuid4()
        date = datetime.now()
        content = "a github post"
        
        
        self.assertEqual(GithubPosts.objects.all().count(), 0)
        # create a github post (mark a post as being a github post)
        githubPost = GithubPosts.objects.get_or_create(post_id=post, gh_uuid=gh_uuid, content=content, date=date)[0]
    
        # check that the github post exists
        self.assertEqual(GithubPosts.objects.filter(post_id=post, content="a github post")[0], githubPost)
        self.assertEqual(GithubPosts.objects.all().count(), 1)


    # CREATE A GITHUB POST WITHOUR REFERENCING THE POST
    def test_create_githubpost_without_post(self):
    
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="thought-bubble.com", email="marcu@ualberta.ca", github="marcugit")[0]
    
        gh_uuid = uuid.uuid4()
        date = datetime.now()
        content = "a github post without post"
    
        self.assertEqual(GithubPosts.objects.all().count(), 0)
    
        # try to create github post without a post
        try:
            githubPost = GithubPosts.objects.get_or_create(gh_uuid=gh_uuid, content=content, date=date)[0]
        except:
            githubPost = "No post"
    
        # check github post not created
        self.assertEqual(githubPost, "No post")
        self.assertFalse(GithubPosts.objects.filter(content="a github post without post"))
        self.assertEqual(GithubPosts.objects.all().count(), 0)

    # UPDATE A GITHUB POST'S CONTENT
    def test_update_post(self):
    
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="thought-bubble.com", email="marcu@ualberta.ca")[0]
        
        post = Posts.objects.get_or_create(author_id=author, title="First Post", content="the first post", privacy="public")[0]
    
        gh_uuid = uuid.uuid4()
        date = datetime.now()
        content = "a github post"
        githubPost = GithubPosts.objects.get_or_create(post_id=post, gh_uuid=gh_uuid, content=content, date=date)[0]
    
        self.assertEqual(GithubPosts.objects.all().count(), 1)
    
        # retrieve an existing github post, update the content, and save
        githubPost = GithubPosts.objects.get(post_id=post, content="a github post")
        githubPost.content = "This is Github"
        githubPost.save()
    
        # check that record is updated
        self.assertEqual(GithubPosts.objects.filter(post_id=post, content="This is Github")[0], githubPost)
        # check that previous record does not exist
        self.assertFalse(GithubPosts.objects.filter(post_id=post, content="a github post"))
        self.assertEqual(GithubPosts.objects.all().count(), 1)

    # DELETE A GITHUB POST
    def test_delete_post(self):
    
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="thought-bubble.com", email="marcu@ualberta.ca")[0]
        post = Posts.objects.get_or_create(author_id=author, title="First Post", content="the first post", privacy="public")[0]
    
        gh_uuid = uuid.uuid4()
        date = datetime.now()
        content = "a github post"
        githubPost = GithubPosts.objects.get_or_create(post_id=post, gh_uuid=gh_uuid, content=content, date=date)[0]
    
        self.assertEqual(Posts.objects.all().count(), 1)
        self.assertEqual(GithubPosts.objects.all().count(), 1)
    
        # retrieve an existing post and delete
        GithubPosts.objects.get(post_id=post, content="a github post").delete()
        Posts.objects.get(author_id=author, content="the first post").delete()
    
        try:
            deleted = GithubPosts.objects.get(post_id=post, content="a github post")
        except:
            deleted = "deleted"
    
        # check the post does not exist
        self.assertEqual(deleted, "deleted")
        self.assertEqual(GithubPosts.objects.all().count(), 0)
        self.assertEqual(Posts.objects.all().count(), 0)



# FRIENDS TESTS
class FriendsTests(TestCase):
    
    # CREATE FOLLOWS (friends with unconfirmed friend request) AND FIRENDS (friends with confirmed friend request) (status: false=follow, true=friend)
    def test_create_follows(self):
        
        author1 = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="thought-bubble.com", email="marcu@ualberta.ca")[0]
        author2 = Authors.objects.get_or_create(name="Bob Murley", username="bobmurley",location="thought-bubble.com", email="murley@ualberta.ca")[0]
        
        self.assertEqual(Friends.objects.all().count(), 0)
        
        # friendship relationship as an author 'follows' another (inviter_follow=true)
        follows = Friends.objects.get_or_create(inviter_id=author1, invitee_id=author2, inviter_follow=True)[0]
        
        # check followship created
        self.assertEqual(Friends.objects.filter(inviter_id=author1, invitee_id=author2, inviter_follow=True)[0], follows)
        self.assertEqual(Friends.objects.all().count(), 1)
        
    # CREATE A 'FRIEND REQUEST SENT' RECORD
    def test_create_friend_request(self):
        
        author1 = Authors.objects.get_or_create(name="Adam Smith", username="adamsmith",location="thought-bubble.com", email="smith@ualberta.ca")[0]
        author2 = Authors.objects.get_or_create(name="Alexa Roui", username="alexaroui",location="thought-bubble.com", email="roui@ualberta.ca")[0]
        
        # friendship relationship as inviter friend requests invitee (frequest=true)
        friends = Friends.objects.get_or_create(inviter_id=author1, invitee_id=author2, inviter_follow=True, frequest=True, status=False)[0]
        
        # check friendship created
        self.assertEqual(Friends.objects.filter(inviter_id=author1, invitee_id=author2, frequest=True)[0], friends)
        self.assertEqual(Friends.objects.all().count(), 1)
        

    # UPDATE A FRIENDSHIP (change the status to accept friend request)
    def test_accept_friend_reuquest(self):
    
        author1 = Authors.objects.get_or_create(name="Adam Smith", username="adamsmith",location="thought-bubble.com", email="smith@ualberta.ca")[0]
        author2 = Authors.objects.get_or_create(name="Alexa Roui", username="alexaroui",location="thought-bubble.com", email="roui@ualberta.ca")[0]
    
        friends = Friends.objects.get_or_create(inviter_id=author1, invitee_id=author2, inviter_follow=True, frequest=True, status=False)[0]
    
        self.assertEqual(Friends.objects.filter(inviter_id=author1, invitee_id=author2, frequest=True, status=False)[0], friends)
        self.assertEqual(Friends.objects.all().count(), 1)
    
        # retrieve existing friendship (with false status), update status, and save
        friends = Friends.objects.get(inviter_id=author1, invitee_id=author2)
        friends.status=True
        friends.save()
    
        # check that record is updated
        self.assertEqual(Friends.objects.filter(inviter_id=author1, invitee_id=author2, status=True)[0], friends)
        # check that previous record does not exist
        self.assertFalse(Friends.objects.filter(inviter_id=author1, invitee_id=author2, status=False))
        self.assertEqual(Friends.objects.all().count(), 1)


    # CREATE AN EXISTING FRIENDSHIP ('unique together' constraint)
    def test_create_duplicate_friendship(self):
        
        author1 = Authors.objects.get_or_create(name="Adam Smith", username="adamsmith",location="thought-bubble.com", email="smith@ualberta.ca")[0]
        author2 = Authors.objects.get_or_create(name="Alexa Roui", username="alexaroui",location="thought-bubble.com", email="roui@ualberta.ca")[0]
        
        friends = Friends.objects.get_or_create(inviter_id=author1, invitee_id=author2, status=True)[0]
        self.assertEqual(Friends.objects.all().count(), 1)
        
        # try to create a duplicate friendship
        try:
            with transaction.atomic():
                sameFriends = Friends.objects.create(inviter_id=author1, invitee_id=author2, status=True)[0]
        except IntegrityError:
            sameFriends = "Not unique together"
        
        # check duplicate friendship not created
        self.assertEqual(sameFriends, "Not unique together")
        self.assertEqual(Friends.objects.all().count(), 1)
    
    
    # CREATE FRIENDS WITHOUT REFERENCING SECOND AUTHOR
    def test_create_friends_one_author(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="local", email="marcu@ualberta.ca")[0]
        
        self.assertEqual(Friends.objects.all().count(), 0)
        
        # try to create friendship with only one author
        try:
            friends = Friends.objects.get_or_create(inviter_id=author, status=True)[0]
        except:
            friends = "Need second author"
        
        # check friendship not created
        self.assertEqual(friends, "Need second author")
        self.assertEqual(Friends.objects.all().count(), 0)
    
    
    # DELETE FRIENDS
    def test_delete_friends(self):
        
        author1 = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="local", email="marcu@ualberta.ca")[0]
        author2 = Authors.objects.get_or_create(name="Bob Murley", username="bobmurley",location="local", email="murley@ualberta.ca")[0]
        
        friends = Friends.objects.get_or_create(inviter_id=author1, invitee_id=author2, status=True)[0]
        
        self.assertEqual(Friends.objects.all().count(), 1)
        
        # retrieve a friendship and delete
        Friends.objects.get(inviter_id=author1, invitee_id=author2, status=True).delete()
        
        try:
            deleted = Friends.objects.get(inviter_id=author1, invitee_id=author2, status=True)
        except:
            deleted = "deleted"
        
        # check friendship deleted
        self.assertEqual(deleted, "deleted")
        self.assertEqual(Friends.objects.all().count(), 0)


# COMMENTS TESTS
class CommentsTests(TestCase):
    
    # CREATE COMMENT FOR POST FROM AUTHOR
    def test_create_comment(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu", location="thought-bubble.com", email="marcu@ualberta.ca")[0]
        
        post = Posts.objects.get_or_create(author_id=author, title="A Post", content="this is a post", privacy="public")[0]
        
        self.assertEqual(Comments.objects.all().count(), 0)
        
        # create comment for existing author, existing post
        comment = Comments.objects.get_or_create(author_id=author, post_id=post, content="Writing a comment", date=timezone.now())[0]
        
        # check comment created
        self.assertEqual(Comments.objects.filter(author_id=author, post_id=post, content="Writing a comment")[0], comment)
        self.assertEqual(Comments.objects.all().count(), 1)
    
    # CREATE COMMENT WITHOUT REFERENCING AUTHOR OR POST
    def test_create_comment_without_author_post(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu", location="thought-bubble.com", email="marcu@ualberta.ca")[0]
        
        post = Posts.objects.get_or_create(author_id=author, title="A Post", content="this is a post", privacy="public")[0]
        
        self.assertEqual(Comments.objects.all().count(), 0)
        
        # try to create comment without referencing author
        try:
            comment = Comments.objects.get_or_create(post_id=post, content="Writing a comment")
        
        except:
            comment = "No author"
        
        # check comment not created
        self.assertTrue(comment, "No author")
        self.assertEqual(Comments.objects.all().count(), 0)
        
        # try to create comment without referencing post
        try:
            comment = Comments.objects.get_or_create(author_id=author, content="Writing a comment")
        except:
            comment = "No post"
        
        # check comment not created
        self.assertTrue(comment, "No post")
        self.assertEqual(Comments.objects.all().count(), 0)
    
    # UPDATE COMMENT'S CONTENT
    def test_update_comment(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu", location="thought-bubble.com", email="marcu@ualberta.ca")[0]
        
        post = Posts.objects.get_or_create(author_id=author, title="A Post", content="this is a post", privacy="public")[0]
        
        comment = Comments.objects.get_or_create(author_id=author, post_id=post, content="Writing a comment")[0]
        
        self.assertEqual(Comments.objects.filter(author_id=author, post_id=post, content="Writing a comment")[0], comment)
        self.assertEqual(Comments.objects.all().count(), 1)
        
        # retrieve an existing comment, update content, and save
        comment = Comments.objects.get(author_id=author, post_id=post, content="Writing a comment")
        comment.content = "Updating comment"
        comment.save()
        
        # check that record is updated
        self.assertEqual(Comments.objects.filter(author_id=author, post_id=post, content="Updating comment")[0], comment)
        # check that previous record does not exist
        self.assertFalse(Comments.objects.filter(author_id=author, post_id=post, content="Writing a comment"))
        self.assertEqual(Comments.objects.all().count(), 1)
    
    # DELETE COMMENT
    def test_delete_comment(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu", location="thought-bubble.com", email="marcu@ualberta.ca")[0]
        
        post = Posts.objects.get_or_create(author_id=author, title="A Post", content="this is a post", privacy="public")[0]
        
        comment = Comments.objects.get_or_create(author_id=author, post_id=post, content="Writing a comment", date=timezone.now())[0]
        
        self.assertEqual(Comments.objects.all().count(), 1)
        
        # retrieve an existing comment and delete
        Comments.objects.get(author_id=author, post_id=post, content="Writing a comment").delete()
        
        try:
            deleted = Comments.objects.get(author_id=author, post_id=post, content="Writing a comment")
        except:
            deleted = "deleted"
        
        # check comment deleted
        self.assertEqual(deleted, "deleted")
        self.assertEqual(Comments.objects.all().count(), 0)



# DELETE AUTHOR, DELETE ON CASCADE
class DeleteTests(TestCase):
    
    # DELETE AUTHOR DELETE ON CASCADE - friends/posts/comments that reference the author
    def test_delete_on_cascade(self):
        
        author1 = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu", location="thought-bubble.com", email="marcu@ualberta.ca")[0]
        author2 = Authors.objects.get_or_create(name="Bob Murley", username="bobmurley", location="thought-bubble.com", email="murley@ualberta.ca")[0]
        
        post = Posts.objects.get_or_create(author_id=author1, title="First Post", content="the post content", privacy="public")[0]
        
        comment = Comments.objects.get_or_create(author_id=author1, post_id=post, content="Writing a comment")[0]
        
        friends = Friends.objects.get_or_create(inviter_id=author1, invitee_id=author2, status=True)[0]
        
        # two authors exist, a friendship relationship, and a post and comment of one author
        self.assertEqual(Authors.objects.all().count(), 2)
        self.assertEqual(Posts.objects.all().count(), 1)
        self.assertEqual(Comments.objects.all().count(), 1)
        self.assertEqual(Friends.objects.all().count(), 1)
        
        # delete one author
        Authors.objects.get(username = "anamarcu", location="thought-bubble.com").delete()
        
        # check only one author exists
        # check friendship/post/comment do not exist
        self.assertEqual(Authors.objects.all().count(), 1)
        self.assertEqual(Posts.objects.all().count(), 0)
        self.assertEqual(Comments.objects.all().count(), 0)
        self.assertEqual(Friends.objects.all().count(), 0)







