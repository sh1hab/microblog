from myapp import mail
from flask import render_template, current_app
from flask_mail import Message
from threading import Thread


def send_async_email(application, msg):
    with application.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body, attachments=None, sync=False) -> object:
    """

    :rtype: object
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    if attachments:
        for attachment in attachments:
            # func(*args) = func()
            msg.attach(*attachment)

    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()  # background thread


def send_password_reset_email(user) -> object:
    token = user.get_reset_password_token()
    send_email(subject='[MicroBlog] Reset your password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token)
               )
