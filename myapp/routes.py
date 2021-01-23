from myapp import db
from myapp import application
from myapp.forms import LoginForm, RegistrationForm
from myapp.models import User
from werkzeug.urls import url_parse
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required


# decorator
@application.route('/login', methods=['GET', 'POST'])
def login():  # view function
    if current_user.is_authenticated:
        return redirect((url_for('index')))
    form = LoginForm()
    if form.validate_on_submit():  # checks if form is submitted & validated
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next', 'indexpage')
        print(url_parse(next_page))
        if not next_page or url_parse(next_page).netloc != '':  # To determine if the URL is relative or absolute
            next_page = url_for('index')
        flash('login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        return redirect(next_page)  # returns the url of view function from routes file
    return render_template('login.html', title='sign in', form=form)


@application.route('/register', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='register', form=form)


@application.route('/logout', methods=['GET'])
def logout():
    if current_user.is_authenticated:
        # user = User.query.filter_by(username=form.username.data).first()
        logout_user()
        return redirect(url_for('login'))
    else:
        return redirect(url_for('index'))


@application.route('/')
@application.route('/indexpage')  # default method GET
@login_required
def index():
    user = {'username': 'shihab'}
    users = User.query.all()
    posts = [
        {
            'author': {'username': 'john'},
            'body': 'beautiful day in portland!'
        },
        {
            'author': {'username': 'doe'},
            'body': 'beautiful day in doeland!'
        },
    ]
    return render_template('index.html', title='Home', users=users, posts=posts)
