# like index.php file
from myapp import application, db
from myapp.models import User, Post, UserDetails


@application.shell_context_processor
def make_shell_context():
    # returns dictionary
    return {'db': db, 'User': User, 'Post': Post, 'userdetails': UserDetails}
