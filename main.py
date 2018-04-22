from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import traceback

app = Flask(__name__)
app.config['DEBUG'] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(40))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['GET','POST'])
def index():

    blogs = Blog.query.all()
    return render_template("blogs.html", blogs=blogs)

@app.route("/blog", methods=['GET','POST'])
def blogs():
    #post = Blog.query.get('id')
    blog_id = request.args.get('id')
    post=Blog.query.get(blog_id)
    #print(post)
    #print('6'*500)
    return render_template('individual_entry.html', title=post.title, post=post)
'''
@app.route("/blog/<blog_id>", methods=['POST', 'GET'])
def indvidual_blogpost(blog_id):
    post = Blog.query.get(blog_id)
    #post = request.args.get('id')
    #print(post)
    #print('6'*500)
    return render_template('individual_entry.html', title=post.title, post=post)
'''

@app.route("/newblog", methods=['POST', 'GET'])
def index2():
    title_error=''
    body_error=''
    blogs = Blog.query.all()

    print(blogs)

    try:
        if request.method == 'POST':

            blog_body = request.form['blog_body']
            blog_name = request.form['blog_name']
            new_blog = Blog(blog_name, blog_body)
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
                    body_error=body_error, title_error=title_error, blog_body=blog_body, blog_name=blog_name)

        else:
            return render_template('newblog.html', title="New Blog", blogs=blogs,)

            
    except Exception:
            traceback.print_exc()

if __name__ == '__main__':
    app.run()
