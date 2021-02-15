# from filename import Classname
import os

from flask import Flask  # loads flask
from config import Config  # loads configuration
from flask_sqlalchemy import SQLAlchemy  # manages sql
from flask_migrate import Migrate  # manages migrate
from flask_login import LoginManager
from logging.handlers import SMTPHandler
import logging
from logging.handlers import RotatingFileHandler
from flask_mail import Mail
from flask_bootstrap import Bootstrap

application = Flask(__name__)  # loading application package __name__ = myapp
# application is a variable which is a instance of Flask application
application.config.from_object(Config)  # loading configuration
db = SQLAlchemy(application)  # SQLAlchemy orm - object relational mapper
migrate = Migrate(application, db)
login = LoginManager(application)
login.login_view = 'login'
mail = Mail(application)
bootstrap = Bootstrap(application)

if not application.debug:
    if application.config['MAIL_SERVER']:
        auth = None
        if application.config['MAIL_USERNAME'] or application.config['MAIL_PASSWORD']:
            auth = (application.config['MAIL_USERNAME'])
        secure = None
        if application.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(application.config['MAIL_SERVER'], application.config['MAIL_PORT']),
            fromaddr='no-reply@' + application.config['MAIL_SERVER'],
            toaddrs=application.config['ADMINS'], subject=os.environ.get('application_name'),
            credentials=auth,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        application.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=102400, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    application.logger.addHandler(file_handler)
    application.logger.setLevel(logging.INFO)
    application.logger.info('microBlog startup')

# circular import issue
# common problem in flask myapp
# routes model is importing
from myapp import routes, models, errors
