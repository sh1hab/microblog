from myapp import db
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from myapp import login
from hashlib import md5
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # 1st arg class name,
    # 2nd arg will be added to posts class object,
    # 3rd arg lazy argument defines how the database query for the relationship will be issued
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    userDetails = db.relationship('UserDetails', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())

    # debugging purpose
    def __repr__(self):
        return '<User {}>'.format(self.username)

    # validation
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # validation
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        # print(self.email, self.username)
        if self.email is not None:
            digest = md5(self.email.lower().encode('utf-8')).hexdigest()
            return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
        else:
            return 'https://www.gravatar.com/avatar'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # ForeignKey

    def __repr__(self):
        return '<Post {}'.format(self.body)


class UserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    address = db.Column(db.String())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@login.user_loader
def load_user(id):
    return User.query.get((int(id)))
