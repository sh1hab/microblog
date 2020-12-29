from app import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    # 1st arg class name,
    # 2nd arg will be added to posts class object,
    # 3rd arg lazy argument defines how the database query for the relationship will be issued
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    # debugging purpose
    def __repr__(self):
        return '<User {}>'.format(self.username)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))   # ForeignKey

    def __repr__(self):
        return '<Post {}'.format(self.body)
