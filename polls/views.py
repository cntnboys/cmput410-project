from django.shortcuts import render

from polls.models import Authors, Friends, Posts, Comments, GithubStreams, TwitterStreams, FacebookStreams


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