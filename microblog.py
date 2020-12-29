# like index.php file
from app import application, db
from app.models import User, Post


@application.shell_context_processor
def make_shell_context():
    # returns dictionary
    return {'db': db, 'User': User, 'Post': Post}
