from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, g, jsonify, current_app
from werkzeug.urls import url_parse
from myapp import db
from myapp.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, \
    ResetPasswordForm
from myapp.models import User
from myapp.email import send_password_reset_email
from flask_babel import _, get_locale
from flask_login import current_user, login_user, logout_user
from myapp.auth import bp


# important
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.locale = str(get_locale())


# decorator
@bp.route('/login', methods=['GET', 'POST'])
def login():  # view function
    if current_user.is_authenticated:
        return redirect((url_for('main.index')))
    form = LoginForm()
    if form.validate_on_submit():  # checks if form is submitted & validated
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next', 'index')
        # print(url_parse(next_page))
        if not next_page or url_parse(next_page).netloc != '':  # To determine if the URL is relative or absolute
            next_page = url_for('main.index')
        flash('login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        return redirect(next_page)  # returns the url of view function from routes file
    return render_template('auth/login.html', title='sign in', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='register', form=form)


@bp.route('/logout', methods=['GET'])
def logout():
    if current_user.is_authenticated:
        # user = User.query.filter_by(username=form.username.data).first()
        logout_user()
        flash(_('You have logged out'))
        return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('main.index'))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('check your email for the instructions to reset your password')
        else:
            flash('user not found')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
