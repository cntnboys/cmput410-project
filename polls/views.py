import calendar
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.forms import EmailField

from polls.models import Authors, Friends, Posts, Comments, GithubStreams, TwitterStreams, FacebookStreams

# TODO: Fix the template pathing using settings.py
def mainPage(request):
	return render(request, 'intro.html')

def redirectMain(request):
	return redirect(mainPage)

def loginPage(request):
	return render(request, 'login.html')

def editProfileMain(request):
	return render(request, 'profile.html')

def registerPage(request):
	return render(request, 'Register.html')

# Create your views here.
#@app.route('/mainpage', methods = ['GET', 'POST'])
#def post():
#    if request.method == 'POST' :
#        if not session.get('logged_in'):
#            abort(401)
#        post = request.form['post']
#        add_post(postid, authorid, ,content, image, privacy)
#        flash('New post was successfully added.')
#        return redirect(url_for('mainpage'))
#    posts = query_db('SELECT * FROM posts')
#    return render_template('mainpage.html', posts=posts)

#def add_post(postid, authorid, ,content, image, privacy):
#    query_db("insert into posts(post_id, author_id, ,content, image, privacy) values(?,?,?,?,?)", (postid, authorid, ,content, image, privacy))
#    get_conn().commit();