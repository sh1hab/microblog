from flask import Blueprint

bp = Blueprint('errors', __name__)
from myapp.errors import handlers
