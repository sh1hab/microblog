from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from myapp import application
from myapp import db
from myapp.forms import LoginForm, RegistrationForm, EmptyForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from myapp.models import User, Post
from myapp.email import send_password_reset_email

# important
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
        next_page = request.args.get('next', 'index')
        # print(url_parse(next_page))
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


@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])  # default method GET
@login_required
def index():
    # user = {'username': 'shihab'}
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live')
        return redirect(url_for('index'))
    users = User.query.all()
    # posts = [
    #     {
    #         'author': {'username': 'john'},
    #         'body': 'beautiful day in portland!'
    #     },
    #     {
    #         'author': {'username': 'doe'},
    #         'body': 'beautiful day in doeLand!'
    #     },
    # ]
    page = request.args.get('page', 1, type=int)
    # posts = current_user.followed_posts().all()
    posts = current_user.followed_posts().paginate(page, application.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html', title='Home', users=users, posts=posts.items, form=form, next_url=next_url,
                           prev_url=prev_url)


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


@application.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, application.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)


@application.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('check your email for the instructions to reset your password')
        else:
            flash('user not found')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)


@application.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
