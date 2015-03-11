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

from django.db import IntegrityError
from django.db import transaction

from django.utils import timezone
import uuid


from django.test import TestCase

from main.models import Authors, Friends, Posts, Comments

# AUHTOR TESTS
class AuthorTests(TestCase):
    
    # create two authors
    def test_create_author(self):
        
        self.assertEqual(Authors.objects.all().count(), 0)
        
        name = "Ana Marcu"
        username = "aname"
        email = "marcu@ualberta.ca"
        location = "local"
        
        author1 = Authors.objects.get_or_create(name=name, username=username,location=location, email=email, image="/path/to/image.jpg", github="MyGithub", twitter="MyTwitter", facebook="MyFacebook")[0]
        
        self.assertEqual(Authors.objects.filter(username="aname")[0], author1)
        self.assertEqual(Authors.objects.all().count(), 1)
        
        name = "Bob Murley"
        username = "bobmurley"
        email = "murley@ualberta.ca"
        location = "local"
        
        author2 = Authors.objects.get_or_create(name=name, username=username,location=location, email=email)[0]
        
        self.assertEqual(Authors.objects.filter(username="bobmurley")[0], author2)
        self.assertEqual(Authors.objects.all().count(), 2)
    
    
    # create an author with an existing username, and an author with an existing email
    def test_create_same_username_email_author(self):
        
        author2 = Authors.objects.get_or_create(name="Bob Murley", username="bobmurley",location="local", email="murley@ualberta.ca")[0]
        
        self.assertEqual(Authors.objects.all().count(), 1)
        
        name = "Bill Murley"
        username1 = "billmurey"
        username2 = "bobmurley"
        email1 = "murley@ualberta.ca"
        email2 = "bob@ualberta.ca"
        location = "local"
        
        try:
            author3 = Authors.objects.get_or_create(name=name, username=username1,location=location, email=email1)[0]
        except:
            author3 = "Email not unique"
        
        self.assertEqual(author3, "Email not unique")
        self.assertEqual(Authors.objects.all().count(), 1)
        
        try:
            author4 = Authors.objects.get_or_create(name=name, username=username2,location=location, email=email2)[0]
        except:
            author4 = "Username not unique"
        
        self.assertEqual(author4, "Username not unique")
        self.assertEqual(Authors.objects.all().count(), 1)
    
    
    # update and author's username and save
    def test_update_author(self):
        
        author1 = Authors.objects.get_or_create(name="Ana Marcu", username="aname",location="local", email="marcu@ualberta.ca")[0]
        
        self.assertEqual(Authors.objects.filter(username="aname")[0], author1)
        self.assertEqual(Authors.objects.all().count(), 1)
        
        author = Authors.objects.get(username = "aname")
        author.username = "anamarcu"
        author.save()
        
        self.assertEqual(Authors.objects.filter(username="anamarcu")[0], author)
        self.assertFalse(Authors.objects.filter(username="aname"))
        self.assertEqual(Authors.objects.all().count(), 1)
    
    # delete an author
    def test_delete_author(self):
        
        author = Authors.objects.get_or_create(name="Bob Murley", username="bobmurley",location="local", email="murley@ualberta.ca")[0]
        
        self.assertEqual(Authors.objects.all().count(), 1)
        
        Authors.objects.get(username = "bobmurley").delete()
        
        try:
            deleted = Authors.objects.get("username = bobmurley")
        except:
            deleted = None
        
        self.assertEqual(deleted, None)
        self.assertEqual(Authors.objects.all().count(), 0)




# POSTS TESTS
class PostsTests(TestCase):
    
    # create two posts for an author
    def test_create_post(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="local", email="marcu@ualberta.ca")[0]
        
        self.assertEqual(Posts.objects.all().count(), 0)
        
        title = "First Post"
        content = "the first post"
        privacy = "public"
        
        post1 = Posts.objects.get_or_create(author_id=author, title=title, content=content, privacy=privacy, image="/path/to/image.jpg")[0]
        
        self.assertEqual(Posts.objects.filter(author_id=author, title="First Post", privacy="public")[0], post1)
        self.assertEqual(Posts.objects.all().count(), 1)
        
        title = "Second Post"
        content = "the second post"
        privacy = "private"
        
        
        post2 = Posts.objects.get_or_create(author_id=author, title=title, content=content, privacy=privacy)[0]
        
        self.assertEqual(Posts.objects.filter(author_id=author, title="Second Post", privacy="private")[0], post2)
        self.assertEqual(Posts.objects.all().count(), 2)
    
    
    # create a post without specifying the author
    def test_create_post_without_author(self):
        
        self.assertEqual(Posts.objects.all().count(), 0)
        
        title = "Third Post"
        content = "the third post"
        privacy = "public"
        
        try:
            post = Posts.objects.get_or_create(title=title, content=content, privacy=privacy)[0]
        except:
            post = "No author"
        
        self.assertEqual(post, "No author")
        self.assertFalse(Posts.objects.filter(title="Third Post", privacy="public"))
        self.assertEqual(Posts.objects.all().count(), 0)
    
    # update a post's content text
    def test_update_post(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="local", email="marcu@ualberta.ca")[0]
        post1 = Posts.objects.get_or_create(author_id=author, title="First Post", content="the first post", privacy="public")[0]
        
        self.assertEqual(Posts.objects.filter(author_id=author, content="the first post", privacy="public")[0], post1)
        self.assertEqual(Posts.objects.all().count(), 1)
        
        post = Posts.objects.get(author_id=author, title="First Post", privacy="public")
        post.content = "writing post"
        post.privacy = "private"
        post.save()
        
        
        self.assertEqual(Posts.objects.filter(author_id=author, content="writing post", privacy="private")[0], post)
        self.assertFalse(Posts.objects.filter(author_id=author, content="the first post", privacy="public"))
        self.assertEqual(Posts.objects.all().count(), 1)
    
    # delete a post
    def test_delete_post(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="local", email="marcu@ualberta.ca")[0]
        post = Posts.objects.get_or_create(author_id=author, title="First Post", content="the first post", privacy="public")[0]
        
        
        self.assertEqual(Posts.objects.all().count(), 1)
        
        Posts.objects.get(author_id=author, content="the first post", privacy="public").delete()
        
        try:
            deleted = Posts.objects.get(author_id=author, content="the first post", privacy="public")
        except:
            deleted = "deleted"
        
        self.assertEqual(deleted, "deleted")
        self.assertEqual(Posts.objects.all().count(), 0)

# FRIENDS TESTS
class FriendsTests(TestCase):
    
    # create follows (friends with unconfirmed friend request) and friends (friends with confirmed friend request) (status: false=follow, true=friend)
    def test_create_friends(self):
        
        author1 = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="local", email="marcu@ualberta.ca")[0]
        author2 = Authors.objects.get_or_create(name="Bob Murley", username="bobmurley",location="local", email="murley@ualberta.ca")[0]
        author3 = Authors.objects.get_or_create(name="Adam Smith", username="adamsmith",location="local", email="smith@ualberta.ca")[0]
        author4 = Authors.objects.get_or_create(name="Alexa Roui", username="alexaroui",location="local", email="roui@ualberta.ca")[0]
        
        self.assertEqual(Friends.objects.all().count(), 0)
        
        follows = Friends.objects.get_or_create(inviter_id=author1, invitee_id=author2, status=False)[0]
        
        self.assertEqual(Friends.objects.filter(inviter_id=author1, invitee_id=author2, status=False)[0], follows)
        self.assertEqual(Friends.objects.all().count(), 1)
        
        friends = Friends.objects.get_or_create(inviter_id=author3, invitee_id=author4, status=True)[0]
        
        self.assertEqual(Friends.objects.filter(inviter_id=author3, invitee_id=author4, status=True)[0], friends)
        self.assertEqual(Friends.objects.all().count(), 2)
        
        try:
            with transaction.atomic():
                sameFriends = Friends.objects.create(inviter_id=author3, invitee_id=author4, status=True)
        except IntegrityError:
            sameFriends = "Not unique together"
        
        self.assertEqual(sameFriends, "Not unique together")
        self.assertEqual(Friends.objects.all().count(), 2)
    
    
    # create friends without specifying a second author
    def test_create_friends_one_author(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="local", email="marcu@ualberta.ca")[0]
        
        self.assertEqual(Friends.objects.all().count(), 0)
        
        try:
            friends = Friends.objects.get_or_create(inviter_id=author, status=True)[0]
        except:
            friends = "Need second author"
        
        self.assertEqual(friends, "Need second author")
        self.assertEqual(Friends.objects.all().count(), 0)
    
    # update a friends record, change from follow to friends (as if confirm request)
    def test_update_friends(self):
        
        author1 = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="local", email="marcu@ualberta.ca")[0]
        author2 = Authors.objects.get_or_create(name="Bob Murley", username="bobmurley",location="local", email="murley@ualberta.ca")[0]
        
        follows = Friends.objects.get_or_create(inviter_id=author1, invitee_id=author2, status=False)[0]
        
        self.assertEqual(Friends.objects.filter(inviter_id=author1, invitee_id=author2, status=False)[0], follows)
        self.assertEqual(Friends.objects.all().count(), 1)
        
        
        friends = Friends.objects.get(inviter_id=author1, invitee_id=author2)
        friends.status=True
        friends.save()
        
        
        self.assertEqual(Friends.objects.filter(inviter_id=author1, invitee_id=author2, status=True)[0], friends)
        self.assertFalse(Friends.objects.filter(inviter_id=author1, invitee_id=author2, status=False))
        self.assertEqual(Friends.objects.all().count(), 1)
    
    # delete friends
    def test_delete_friends(self):
        
        author1 = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="local", email="marcu@ualberta.ca")[0]
        author2 = Authors.objects.get_or_create(name="Bob Murley", username="bobmurley",location="local", email="murley@ualberta.ca")[0]
        
        friends = Friends.objects.get_or_create(inviter_id=author1, invitee_id=author2, status=True)[0]
        
        self.assertEqual(Friends.objects.all().count(), 1)
        
        Friends.objects.get(inviter_id=author1, invitee_id=author2, status=True).delete()
        
        try:
            deleted = Friends.objects.get(inviter_id=author1, invitee_id=author2, status=True)
        except:
            deleted = "deleted"
        
        self.assertEqual(deleted, "deleted")
        self.assertEqual(Friends.objects.all().count(), 0)


# COMMENTS TESTS
class CommentsTests(TestCase):
    
    # create a comment from an author for a post
    def test_create_comment(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="local", email="marcu@ualberta.ca")[0]
        
        post = Posts.objects.get_or_create(author_id=author, title="A Post", content="this is a post", privacy="public")[0]
        
        self.assertEqual(Comments.objects.all().count(), 0)
        
        comment = Comments.objects.get_or_create(author_id=author, post_id=post, content="Writing a comment", date=timezone.now())[0]
        
        
        self.assertEqual(Comments.objects.filter(author_id=author, post_id=post, content="Writing a comment")[0], comment)
        self.assertEqual(Comments.objects.all().count(), 1)
    
    # create comment without specifying the author or the post
    def test_create_comment_without_author_post(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="local", email="marcu@ualberta.ca")[0]
        
        post = Posts.objects.get_or_create(author_id=author, title="A Post", content="this is a post", privacy="public")[0]
        
        self.assertEqual(Comments.objects.all().count(), 0)
        
        try:
            comment = Comments.objects.get_or_create(post_id=post, content="Writing a comment", date=timezone.now())
        
        except:
            comment = "No author"
        
        self.assertTrue(comment, "No author")
        self.assertEqual(Comments.objects.all().count(), 0)
        
        try:
            comment = Comments.objects.get_or_create(author_id=author, content="Writing a comment", date=timezone.now())
        except:
            comment = "No post"
        
        self.assertTrue(comment, "No post")
        self.assertEqual(Comments.objects.all().count(), 0)
    
    # update a comment's content
    def test_update_comment(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="local", email="marcu@ualberta.ca")[0]
        
        post = Posts.objects.get_or_create(author_id=author, title="A Post", content="this is a post", privacy="public")[0]
        
        comment = Comments.objects.get_or_create(author_id=author, post_id=post, content="Writing a comment", date=timezone.now())[0]
        
        self.assertEqual(Comments.objects.filter(author_id=author, post_id=post, content="Writing a comment")[0], comment)
        self.assertEqual(Comments.objects.all().count(), 1)
        
        comment = Comments.objects.get(author_id=author, post_id=post, content="Writing a comment")
        comment.content = "Updating comment"
        comment.save()
        
        self.assertEqual(Comments.objects.filter(author_id=author, post_id=post, content="Updating comment")[0], comment)
        self.assertFalse(Comments.objects.filter(author_id=author, post_id=post, content="Writing a comment"))
        self.assertEqual(Comments.objects.all().count(), 1)
    
    # delete a comment
    def test_delete_comment(self):
        
        author = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="local", email="marcu@ualberta.ca")[0]
        
        post = Posts.objects.get_or_create(author_id=author, title="A Post", content="this is a post", privacy="public")[0]
        
        comment = Comments.objects.get_or_create(author_id=author, post_id=post, content="Writing a comment", date=timezone.now())[0]
        
        self.assertEqual(Comments.objects.all().count(), 1)
        
        
        Comments.objects.get(author_id=author, post_id=post, content="Writing a comment").delete()
        
        try:
            deleted = Comments.objects.get(author_id=author, post_id=post, content="Writing a comment")
        except:
            deleted = "deleted"
        
        self.assertEqual(deleted, "deleted")
        self.assertEqual(Comments.objects.all().count(), 0)



# DELETE ON CASCADE WHEN DELETE AUTHOR TESTS
class DeleteTests(TestCase):
    
    # delete author, delete on cascade posts and comments and friends that reference the author
    def test_delete_on_cascade(self):
        
        author1 = Authors.objects.get_or_create(name="Ana Marcu", username="anamarcu",location="local", email="marcu@ualberta.ca")[0]
        author2 = Authors.objects.get_or_create(name="Bob Murley", username="bobmurley",location="local", email="murley@ualberta.ca")[0]
        
        post = Posts.objects.get_or_create(author_id=author1, title="First Post", content="the post content", privacy="public")[0]
        
        comment = Comments.objects.get_or_create(author_id=author1, post_id=post, content="Writing a comment", date=timezone.now())[0]
        
        firends = Friends.objects.get_or_create(inviter_id=author1, invitee_id=author2, status=True)[0]
        
        self.assertEqual(Authors.objects.all().count(), 2)
        self.assertEqual(Posts.objects.all().count(), 1)
        self.assertEqual(Comments.objects.all().count(), 1)
        self.assertEqual(Friends.objects.all().count(), 1)
        
        
        Authors.objects.get(username = "anamarcu").delete()
        
        self.assertEqual(Authors.objects.all().count(), 1)
        self.assertEqual(Posts.objects.all().count(), 0)
        self.assertEqual(Comments.objects.all().count(), 0)
        self.assertEqual(Friends.objects.all().count(), 0)







