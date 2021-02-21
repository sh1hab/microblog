from flask import render_template, flash, redirect, url_for, request
from myapp.models import User
from myapp import application


@application.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)