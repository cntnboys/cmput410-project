import datetime
from django.utils import timezone

from uuidfield import UUIDField

from django.db import models
from django.db import connection

class Authors(models.Model):
    author_id = models.AutoField(primary_key = True)
    author_uuid = UUIDField(auto=True, unique=True)
    name = models.CharField(max_length=200, null=False)
    username = models.CharField(max_length=30, null=False, unique=True)
    image = models.ImageField(upload_to="ProfileImages", max_length=250, null=True)
    email = models.EmailField(max_length=80, null=False, unique=True)
    location = models.CharField(max_length=200, null=False)
    github = models.CharField(max_length=200, null=True)
    twitter = models.CharField(max_length=200, null=True)
    facebook = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = "authors"
        verbose_name = "Author"

    def __str__(self):
        return "author_id: " + str(self.author_id) + " name: " + str(self.name) + " username: " + str(self.username) + " image: " + str(self.image) + " email: " + str(self.email) + " location: " + str(self.location) + " github: " + str(self.github) + " twitter: " + str(self.twitter) + " facebook: " + str(self.facebook)

class Friends(models.Model):
    inviter_id = models.ForeignKey(Authors, related_name='inviter_id', null=False)
    invitee_id = models.ForeignKey(Authors, related_name='invitee_id', null=False)
    status = models.BooleanField(default=False)

    class Meta:
        db_table = "friends"
        verbose_name = "Friend"
        unique_together = (("inviter_id", "invitee_id"),)

    def __str__(self):
        return "inviter_id: " + str(self.inviter_id.author_id) + " invitee_id: " + str(self.invitee_id.author_id) + " status: " + str(self.status)


class Posts(models.Model):
    post_id = models.AutoField(primary_key = True)
    post_uuid = UUIDField(auto=True, unique=True)
    author_id = models.ForeignKey(Authors, db_column="author_id", null=False)
    #author_id = models.CharField(max_length=20, null=False)
    title = models.CharField(max_length=300)
    content = models.CharField(max_length=10000)
    image = models.ImageField(upload_to="PostImages", max_length=250, null=True)
    privacy = models.CharField(max_length=20, null=False)
    date = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        db_table = "posts"
        verbose_name = "Post"

    def __str__(self):
        return "post_id: " + str(self.post_id) + " author_id: " + str(self.author_id.author_id) + " content: " + str(self.content) + " image: " + str(self.image) + " privacy: " + str(self.privacy)


class Comments(models.Model):
    comment_id = models.AutoField(primary_key = True)
    comment_uuid = UUIDField(auto=True, unique=True)
    author_id = models.ForeignKey(Authors, db_column="author_id", null=False)
    date = models.DateTimeField('date posted', null=False)
    post_id = models.ForeignKey(Posts, db_column="post_id", null=False)
    content = models.CharField(max_length=2000, null=True)
    image = models.ImageField(upload_to="ProfileImages", max_length=250, null=True)

    class Meta:
        db_table = "comments"
        verbose_name = "Comment"

    def __str__(self):
        return "author_id: " + str(self.author_id.author_id) + " post_id: " + str(self.post_id.post_id) + " content: " + str(self.content)


class GithubStreams(models.Model):
    gh_id = models.AutoField(primary_key = True)
    gh_uuid = UUIDField(auto=True, unique=True)
    author_id = models.ForeignKey(Authors, db_column="author_id", null=False)
    date = models.DateTimeField('date posted', null=False)
    content = models.CharField(max_length=10000)

    class Meta:
        db_table = "githubstreams"
        verbose_name = "GithubStream"

    def __str__(self):
            return "author_id: " + str(self.author_id.author_id) + " date: " + str(self.date) + " content: " + str(self.content)


class TwitterStreams(models.Model):
    tweet_id = models.AutoField(primary_key = True)
    tweet_uuid = UUIDField(auto=True, unique=True)
    author_id = models.ForeignKey(Authors, db_column="author_id", null=False)
    date = models.DateTimeField('date posted', null=False)
    content = models.CharField(max_length=10000)
    
    class Meta:
        db_table = "twitterstreams"
        verbose_name = "TwitterStream"
       
    def __str__(self):
        return "author_id: " + str(self.author_id.author_id) + " date: " + str(self.date) + " content: " + str(self.content)


class FacebookStreams(models.Model):
    fbstream_id = models.AutoField(primary_key = True)
    fbstream_uuid = UUIDField(auto=True, unique=True)
    author_id = models.ForeignKey(Authors, db_column="author_id", null=False)
    date = models.DateTimeField('date posted', null=False)
    content = models.CharField(max_length=10000)
    
    class Meta:
        db_table = "facebookstreams"
        verbose_name = "FacebookStream"
    
    def __str__(self):
        return "author_id: " + str(self.author_id.author_id) + " date: " + str(self.date) + " content: " + str(self.content)

