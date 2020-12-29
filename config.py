import os

# getting application folder name
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # secret key for CSRF token
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret'   # class variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    # sql alchemy checks if database is updated
    SQLALCHEMY_TRACK_MODIFICATIONS = True
