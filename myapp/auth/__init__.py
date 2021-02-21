from flask import Blueprint

bp = Blueprint('auth', __name__)

from myapp.auth import routes
