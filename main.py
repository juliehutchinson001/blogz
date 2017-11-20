from flask import Flask, session, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '<owiejfnvojfoe8jmm>'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:07131989jSgM@localhost:8889/blogz' #://database-user:password@database_location:port-number/database-name
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(400))
    date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,title,body,owner,date=None):
        self.title = title
        self.body = body
        self.owner = owner
        if date == None:
            date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.date = date

    def __repr__(self):
        # return '<Blog %r>' % self.title
        return '<Blog {!r}>'.format(self.title)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

@app.before_request 
def require_login():
    allowed_routes = ['login','signup','blog','index'] # List of routes user can see without logging in.
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', 
                            title="JHblogz - Home", 
                            users=users)
    
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'GET':
        return render_template('login.html', 
                                title="JHblogz - Login")
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password != user.password:
                flash('bad password', 'error2')
                return redirect("/login")
            elif password == user.password:
                session['username'] = user.username
                return redirect("/new_post")
        flash('bad username', 'error1')
        return redirect("/login")

@app.route('/logout')
def logout():
  del session['username']
  return redirect('/')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == '':
            flash("Please enter a username", 'username_error')
        if password == '':
            flash("Please enter a password", 'password_error')
        if verify == '':
            flash("Passwords don't match", 'verify_error')
    
        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            flash(username + ' is already taken', 'user_taken')
            return redirect('/signup')
        if not password or not username:
            return redirect('/signup')
        if password != verify:
            return redirect('/signup')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        return redirect("/new_post")
    else:
        return render_template('signup.html', 
                                title="JHblogz - Signup")

@app.route('/blog')
def blog():
    blogs = Blog.query.order_by(Blog.date.desc()).all()
    users = User.query.all()

    blog_id = request.args.get('id')
    user_id = request.args.get('user')

    if blog_id:
        single_blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('single_blog.html', 
                                title="JHblogz - All Posts", 
                                base_title="Blogz",
                                single_blog=single_blog)

    if user_id:
        owner = User.query.filter_by(username=user_id).first()
        blogs = Blog.query.filter_by(owner=owner).order_by(Blog.date.desc()).all()
        return render_template('blog.html', 
                                title="JHblogz - All Posts", 
                                base_title="Blogz",
                                blogs=blogs, 
                                users=users)
    else:
        return render_template('blog.html', 
                                title="JHblogz - All Posts", 
                                base_title="Blogz",
                                blogs=blogs, 
                                users=users)


@app.route('/new_post', methods=["POST", "GET"])
def new_post():
    if request.method == "POST":
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        # owner = owner = User.query.filter_by(username=session["username"]).first()
        owner = User.query.filter_by(username=session["username"]).first()
        if blog_title and blog_body:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            blog_id = str(new_blog.id)
            return redirect('/blog?id='+ blog_id)

        if not blog_title:
            flash("Please enter a blog title.", "error1")
        if not blog_body:
            flash("Please enter a blog body.", "error2")
        return redirect('/new_post')
    else:
        return render_template('new_post.html', 
                                title="JHblogz - New Post")

if __name__ == '__main__':
    app.run()