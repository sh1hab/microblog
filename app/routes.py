from app import application
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm


# decorator

@application.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # checks if form is submitted & validated
        flash('login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        return redirect(url_for('index'))   # returns the url of view function from routes file
    return render_template('login.html', title='sign in', form=form)


@application.route('/')
@application.route('/index')  # default method GET
def index():
    user = {'username': 'shihab'}
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
    return render_template('index.html', title='Home', user=user, posts=posts)
