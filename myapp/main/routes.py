from datetime import datetime

from flask import g
from flask import jsonify
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_babel import get_locale
from flask_login import current_user, login_required
from guess_language import guess_language

# from myapp import application
from myapp import db
from myapp.main import bp as main_bp
from myapp.main.forms import EmptyForm, EditProfileForm, PostForm
from myapp.models import User, Post
from myapp.translate import translate


# important
@main_bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.locale = str(get_locale())


@main_bp.route('/', methods=['GET', 'POST'])
@main_bp.route('/index', methods=['GET', 'POST'])  # default method GET
@login_required
def index():
    # user = {'username': 'shihab'}
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live')
        return redirect(url_for('main.index'))
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
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html', title='Home', users=users, posts=posts.items, form=form, next_url=next_url,
                           prev_url=prev_url)


@main_bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id)
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, form=form)


@main_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(original_username=current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes has been saved')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='edit profile', form=form)


@main_bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        searched_user = User.query.filter_by(username=username).first()
        if searched_user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.index'))
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
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@main_bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)


@main_bp.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)


@main_bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({
        'text': translate(request.form['text'],
                          request.form['source_language'],
                          request.form['dest_language'])
    })
