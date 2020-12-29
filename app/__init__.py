# from filename import Classname
from flask import Flask     # loads flask
from config import Config   # loads configuration
from flask_sqlalchemy import SQLAlchemy  # manages sql
from flask_migrate import Migrate  # manages migrate

application = Flask(__name__)  # loading application package __name__ = app
application.config.from_object(Config)  # loading configuration
db = SQLAlchemy(application)    # SQLAlchemy orm - object relational mapper
migrate = Migrate(application, db)

# circular import issue
from app import routes, models

