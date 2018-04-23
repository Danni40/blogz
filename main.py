from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import traceback
import cgi


app = Flask(__name__)
app.config['DEBUG'] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:blogz@localhost:8889/blogz"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(40))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = User.query.filter_by(email=email)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.email
                flash('welcome back, '+user.email)
                return redirect("/newblog")
        flash('bad username or password')
        return redirect("/login")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if not is_email(email):
            flash('zoiks! "' + email + '" does not seem like an email address')
            return redirect('/signup')
        email_db_count = User.query.filter_by(email=email).count()
        if email_db_count > 0:
            flash('yikes! "' + email + '" is already taken and password reminders are not implemented')
            return redirect('/signup')
        if password != verify:
            flash('passwords did not match')
            return redirect('/signup')
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.email
        return redirect("/")
    else:
        return render_template('signup.html')

def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/blog")
'''
@app.route('/', methods=['GET','POST'])
def index():

    blogs = Blog.query.all()
    return render_template("blogs.html", blogs=blogs)
'''
@app.route('/', methods=['GET','POST'])
def index():
    blogs = None
    all_blogs = Blog.query.all()

    data_tuples = []

    user = None
    try:
        if session['logged_in']: 
            blogs = Blog.query.filter(User.id == session["owner_id"])
        else:
            pass
    except KeyError:
        pass

    for blog in all_blogs:
        #grab auth username
        author_object = User.query.get(blog.owner_id)
        author_username = author_object.email
        object_tuple=(blog.title, blog.id, author_username)
        data_tuples.append(object_tuple)
    return render_template('index.html', title="Home", blogs=blogs, user=user, data_tuples=data_tuples)

@app.route("/blog", methods=['GET','POST'])
def blogs():
    #post = Blog.query.get('id')
    blog_id = request.args.get('id')
    post=Blog.query.get(blog_id)
    #print(post)
    #print('6'*500)
    return render_template('individual_entry.html', title=post.title, post=post)

@app.route("/newblog", methods=['POST', 'GET'])
def index2():
    title_error=''
    body_error=''
    blogs = Blog.query.all()
    owner = User.query.filter_by(email=session['user']).first()
    print(blogs)

    try:
        if request.method == 'POST':

            blog_body = request.form['blog_body']
            blog_name = request.form['blog_name']

            new_blog = Blog(blog_name, blog_body, owner)
            db.session.add(new_blog)
            

            if not blog_name:
                title_error='no blog title entered'

            if not blog_body:
                body_error='no blog body entered'

            if not title_error and not body_error:
                db.session.commit()
                blog_id = new_blog.id
                #return redirect('/?id={blog_id}'.format(blog_id=blog_id))
                #return render_template('blogs.html', title="New Blog", blogs=blogs, blog_name=blog_name, blog_body=blog_body)
                return redirect('/')
            else:

                return render_template('newblog.html', title="New Blog", blogs=blogs, 
                    body_error=body_error, title_error=title_error, blog_body=blog_body, blog_name=blog_name, owner=owner)

        else:
            return render_template('newblog.html', title="New Blog", blogs=blogs,)

            
    except Exception:
            traceback.print_exc()

endpoints_without_login = ['login', 'signup','blog', 'index']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/signup")

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == '__main__':
    app.run()
