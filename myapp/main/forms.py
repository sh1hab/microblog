from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length, Email
from myapp.models import User
from flask_babel import lazy_gettext as _l


# class LoginForm(FlaskForm):
#     username = StringField(_l('Username'), validators=[DataRequired()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     remember_me = BooleanField('Remember Me')
#     submit = SubmitField('Sign In')
#
#
# class RegistrationForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired()])
#     email = StringField('email', validators=[DataRequired()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
#     submit = SubmitField('Register')
#
#     def validate_username(self, username):
#         user = User.query.filter_by(username=username.data).first()
#         if user is not None:
#             raise ValidationError('Please use a different username')
#
#     def validate_email(self, email):
#         user = User.query.filter_by(email=email.data).first()
#         if user is not None:
#             raise ValidationError('Please use a different email')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=1, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        # ? super is used to invoke a method in the parent class.
        # In this particular case,
        # I have created a class constructor and
        # I want to invoke the class constructor in the parent class, which is the FlaskForm class.
        # Typically when you override a method in a derived class,
        # you want to invoke the original method in the parent class as well
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            print(self, username.data, user)
            if user is not None:
                raise ValidationError('Please use a different username')


class EmptyForm(FlaskForm):
    submit = SubmitField('submit')


class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('submit')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')
