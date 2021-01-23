# from filename import Classname
from flask import Flask  # loads flask
from config import Config  # loads configuration
from flask_sqlalchemy import SQLAlchemy  # manages sql
from flask_migrate import Migrate  # manages migrate
from flask_login import LoginManager

application = Flask(__name__)  # loading application package __name__ = myapp
# application is a variable which is a instance of Flask application
application.config.from_object(Config)  # loading configuration
db = SQLAlchemy(application)  # SQLAlchemy orm - object relational mapper
migrate = Migrate(application, db)
login = LoginManager(application)
login.login_view = 'login'

# circular import issue
# common problem in flask myapp
# routes model is importing
from myapp import routes, models
