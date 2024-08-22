from quart import Quart
from quart_sqlalchemy import SQLAlchemy

app = Quart(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)


# with app.app_context():
#     db.create_all()

#     db.session.add(User(username="example"))
#     db.session.commit()

#     users = db.session.execute(db.select(User)).scalars()


if __name__ == "__main__":
    app.run()
