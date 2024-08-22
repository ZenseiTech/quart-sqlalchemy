import asyncio
import os
from quart import Quart, render_template, request, redirect, url_for
from dotenv import load_dotenv

from quart_sqlalchemy import SQLAlchemyConfig, Base
from quart_sqlalchemy.framework import QuartSQLAlchemy
from sqlalchemy.orm import mapped_column, relationship
import sqlalchemy as sa


async def initialize(db):
    db.drop_all()
    db.create_all()

    post1 = Post(title='Post The First', content='Content for the first post')
    post2 = Post(title='Post The Second', content='Content for the Second post')
    post3 = Post(title='Post The Third', content='Content for the third post')

    comment1 = Comment(content='Comment for the first post', post=post1)
    comment2 = Comment(content='Comment for the second post', post=post2)
    comment3 = Comment(content='Another comment for the second post', post_id=2)
    comment4 = Comment(content='Another comment for the first post', post_id=1)

    with db.bind.Session() as session:
        with session.begin():
            session.add(post1)
            session.add(post2)
            session.add(post3)

            session.add(comment1)
            session.add(comment2)
            session.add(comment3)
            session.add(comment4)

basedir = os.path.abspath(os.path.dirname(__file__))

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    print("=====******> ", dotenv_path)
    load_dotenv(dotenv_path)

print(os.environ.get('FLASK_COVERAGE'))
if os.environ.get('FLASK_COVERAGE') == 'True':
    print("Coverage....")

app = Quart(__name__)

# postgresql://username:password@host:port/database_name
# mysql://username:password@host:port/database_name

url = 'sqlite:///' + os.path.join(basedir, 'database.db')

config = SQLAlchemyConfig(
        model_class=Base,
        binds={  # type: ignore
            "default": {
                "engine": {"url": url},
                "session": {"expire_on_commit": False},
            },
        },
    )

db = QuartSQLAlchemy(config=config, app=app)


class Post(db.Model):
    id = mapped_column(sa.Integer, primary_key=True)
    title = mapped_column(sa.String(100))
    content = mapped_column(sa.Text)
    comments = relationship('Comment', backref='post')

    def __repr__(self):
        return f'<Post "{self.title}">'


class Comment(db.Model):
    id = mapped_column(sa.Integer, primary_key=True)
    content = mapped_column(sa.Text)
    post_id = mapped_column(sa.Integer, sa.ForeignKey('post.id'))

    def __repr__(self):
        return f'<Comment "{self.content[:20]}...">'


asyncio.run(initialize(db))


@app.get('/')
async def index():
    with db.bind.Session() as s:
        posts = s.scalars(sa.select(Post)).all()
        return await render_template('index.html', posts=posts)


@app.route('/<int:post_id>/', methods=('GET', 'POST'))
async def post(post_id):
    with db.bind.Session() as session:
        stmt = sa.select(Post).where(Post.id == post_id)
        post = session.scalars(stmt).one()
        print(str(post.comments))
        if request.method == 'POST':
            content=(await request.form)['content']
            print("Content =====> " + content)
            comment = Comment(content=content, post_id=post_id)
            session.add(comment)
            session.commit()
            return redirect(url_for('post', post_id=post_id))

    return await render_template('post.html', post=post)


@app.route('/comments/')
async def comments():
    with db.bind.Session() as session:
        rows = session.query(Comment).all()
        comments = []
        for row in rows:
            comment = Comment(id=row.id, content=row.content)
            comments.append(comment)
        
    return await render_template('comments.html', comments=comments)


@app.post('/comments/<int:comment_id>/delete')
async def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post.id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('post', post_id=post_id))


if __name__ == "__main__":
    app.run(port=5001)
