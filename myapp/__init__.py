# from filename import Classname
import os

from flask import Flask  # loads flask
from config import Config  # loads configuration
from flask_sqlalchemy import SQLAlchemy  # manages sql
from flask_migrate import Migrate  # manages migrate
from flask_login import LoginManager  # manages login
from logging.handlers import SMTPHandler
import logging
from logging.handlers import RotatingFileHandler
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel
from flask_babel import lazy_gettext as _l
from elasticsearch import Elasticsearch

# application = Flask(__name__)
# application is a variable which is a instance of Flask application
# application.config.from_object(Config)  # loading configuration
db = SQLAlchemy()  # SQLAlchemy orm - object relational mapper
migrate = Migrate()
login = LoginManager()
# overriding login view
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()


# factory
def create_app(config_class=Config):
    # loading application package __name__ = myapp
    # application is a variable which is a instance of Flask application
    application = Flask(__name__)  # loading application package __name__ = myapp
    application.config.from_object(config_class)  # loading configuration
    db.init_app(application)
    login.init_app(application)
    migrate.init_app(application, db)
    mail.init_app(application)
    bootstrap.init_app(application)
    moment.init_app(application)
    babel.init_app(application)

    # registering blueprint to application
    from myapp.errors import bp as errors_bp
    application.register_blueprint(errors_bp)

    from myapp.auth import bp as auth_bp
    # url_prefix used for route prefix
    application.register_blueprint(auth_bp, url_prefix='/auth')

    from myapp.main import bp as main_bp
    application.register_blueprint(main_bp)

    # loading elasticSearch
    application.elasticsearch = Elasticsearch([application.config['ELASTICSEARCH_URL']]) \
        if application.config['ELASTICSEARCH_URL'] else None

    if not application.debug and not application.testing:
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
        # if logs folder doesn't exist create logs
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microBlog.log', maxBytes=102400, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        application.logger.addHandler(file_handler)
        application.logger.setLevel(logging.INFO)
        application.logger.info('microBlog startup')

    return application


@babel.localeselector
def get_locale():
    # return request.accept_languages.best_match(application.config['LANGUAGES'])
    return 'es'


# circular import issue
# common problem in flask myapp
# routes model is importing
# from myapp import routes, models, errors
from myapp import models
