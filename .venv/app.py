import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from quart import Quart

import init_db
from model import db, Post, Comment

basedir = os.path.abspath(os.path.dirname(__file__))

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    print("=====******> ", dotenv_path)
    load_dotenv(dotenv_path)

print(os.environ.get('FLASK_COVERAGE'))
if os.environ.get('FLASK_COVERAGE') == 'True':
    print("Coverage....")

app = Flask(__name__)

# postgresql://username:password@host:port/database_name
# mysql://username:password@host:port/database_name

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialize the app with the extension
db.init_app(app)

with app.app_context():
    init_db.initialize(db)

    posts = Post.query.all()

    for post in posts:
        print(f'## {post.title}')
        for comment in post.comments:
            print(f'> {comment.content}')
        print('----')


@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/<int:post_id>/', methods=('GET', 'POST'))
def post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        comment = Comment(content=request.form['content'], post=post)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('post', post_id=post.id))

    return render_template('post.html', post=post)


@app.route('/comments/')
def comments():
    comments = Comment.query.order_by(Comment.id.desc()).all()
    return render_template('comments.html', comments=comments)


@app.post('/comments/<int:comment_id>/delete')
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post.id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('post', post_id=post_id))


if __name__ == "__main__":
    app.run()
