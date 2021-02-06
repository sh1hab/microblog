from myapp import db
from myapp import application
from myapp.forms import LoginForm, RegistrationForm, EmptyForm
from myapp.models import User
from werkzeug.urls import url_parse
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime
from myapp.forms import EditProfileForm


@application.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


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
    # user = {'username': 'shihab'}
    users = User.query.all()
    posts = [
        {
            'author': {'username': 'john'},
            'body': 'beautiful day in portland!'
        },
        {
            'author': {'username': 'doe'},
            'body': 'beautiful day in doeLand!'
        },
    ]
    return render_template('index.html', title='Home', users=users, posts=posts)


@application.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, form=form)


@application.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(original_username=current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes has been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='edit profile', form=form)


@application.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        searched_user = User.query.filter_by(username=username).first()
        if searched_user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        elif searched_user != current_user:
            if not current_user.is_following(searched_user):
                current_user.follow(searched_user)
                flash('You are following {}!'.format(username))
            else:
                current_user.unfollow(searched_user)
                flash('You are not following {}!'.format(username))
            db.session.commit()
        else:
            flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

