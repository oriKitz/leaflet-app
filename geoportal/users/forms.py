from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DecimalField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from geoportal.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class PreferencesForm(FlaskForm):
    starting_lon = DecimalField('Starting longitude', rounding=False, places=6)
    starting_lat = DecimalField('Starting latitude', rounding=False, places=6)
    starting_zoom = SelectField('Starting zoom', choices=[(None, '---')] + [(n, n) for n in range(1, 21)])
    submit = SubmitField('Save')


class TeamForm(FlaskForm):
    name = StringField('Team Name', validators=[DataRequired()])
    submit = SubmitField('Register Team')
