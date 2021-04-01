# like index.php file
from flask import current_app
from myapp import db, create_app, cli
from myapp.models import User, Post, UserDetails, Notification, Message, Task
from myapp import cli

# create app
application = create_app()
cli.register(application)


@application.shell_context_processor
def make_shell_context():
    # returns dictionary
    return {'db': db, 'User': User, 'Post': Post, 'userdetails': UserDetails, 'message': Message,
            'notification': Notification, 'task': Task}
