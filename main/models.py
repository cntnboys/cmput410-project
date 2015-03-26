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
    image = models.ImageField(upload_to="ProfileImages", max_length=250, null=True, blank=True)
    email = models.EmailField(max_length=80, null=False, unique=True)
    location = models.CharField(max_length=200, null=False)
    github = models.CharField(max_length=200, null=True, blank=True)

    # For 0 Pending, 1 For True 
    status = models.BooleanField(default=False)

    class Meta:
        db_table = "authors"
        verbose_name = "Author"

    def __str__(self):
        return ("author_id: " + str(self.author_id) + "author_uuid: " + str(self.author_uuid) + 
                " name: " + str(self.name) + " username: " + str(self.username) + " image: " + str(self.image) + 
                " email: " + str(self.email) + " location: " + str(self.location) + " github: " + str(self.github))

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
    title = models.CharField(max_length=300, blank=True)
    content = models.CharField(max_length=10000, blank=True)
    image = models.ImageField(upload_to="PostImages", max_length=250, null=True, blank=True)
    privacy = models.CharField(max_length=20, null=False, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        db_table = "posts"
        verbose_name = "Post"

    def __str__(self):
        return "post_id: " + str(self.post_id) + " author_id: " + str(self.author_id.author_id) + " content: " + str(self.content) + " image: " + str(self.image) + " privacy: " + str(self.privacy)

class Nodes(models.Model):
    node_id = models.AutoField(primary_key = True)
    # We will use this as our host
    node_url = models.CharField(max_length=300, unique=True)
    # Location Name
    node_name = models.CharField(max_length=300)
    # 0 For Pending, 1 For Accepted
    node_status = models.BooleanField(default=False)

    class Meta:
        db_table = "nodes"
        verbose_name = "Node"

    def __str__(self):
        return ( "node_id: " + str(self.node_id) + " node url: " + self.node_url + ' node name: ' +
                 self.node_name + ' node_status: ' + str(self.node_status) )

class Comments(models.Model):
    comment_id = models.AutoField(primary_key = True)
    comment_uuid = UUIDField(auto=True, unique=True)
    author_id = models.ForeignKey(Authors, db_column="author_id", null=False)
    date = models.DateTimeField(auto_now_add=True, null=False)
    post_id = models.ForeignKey(Posts, db_column="post_id", null=False)
    content = models.CharField(max_length=2000, null=True, blank=True)
    image = models.ImageField(upload_to="ProfileImages", max_length=250, null=True, blank=True)

    class Meta:
        db_table = "comments"
        verbose_name = "Comment"

    def __str__(self):
        return "author_id: " + str(self.author_id.author_id) + " post_id: " + str(self.post_id.post_id) + " content: " + str(self.content)


class GithubPosts(models.Model):
    gh_id = models.AutoField(primary_key = True)
    gh_uuid = models.CharField(max_length=100)
    post_id = models.ForeignKey(Posts, db_column="post_id", null=False)
    date = models.DateTimeField('date posted', null=False)
    content = models.CharField(max_length=10000, blank=True)

    class Meta:
        db_table = "githubposts"
        verbose_name = "GithubPosts"

    def __str__(self):
            return "gh_id: " + str(self.gh_id) + "gh_uuid: " + str(self.gh_uuid) + "post_id: " + str(self.post_id.post_id) + " date: " + str(self.date) + " content: " + str(self.content)

