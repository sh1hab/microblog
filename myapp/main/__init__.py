from flask import Blueprint

bp = Blueprint('main', __name__)

from myapp.main import routes
