from flask import render_template, url_for, request, jsonify, redirect, flash, abort, Blueprint
from geoportal import  db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from .forms import RegistrationForm, LoginForm, TeamForm, PreferencesForm
from geoportal.models import User, Team, UserPreferences

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        preferences = UserPreferences(user_id=user.id)
        db.session.add(preferences)
        db.session.commit()
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form, fields=['username', 'email', 'first_name', 'last_name', 'password', 'confirm_password'])


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form, fields=['username', 'password'])


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = PreferencesForm()
    current_preference = UserPreferences.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        print(form.starting_zoom.data)
        current_preference.starting_lon = form.starting_lon.data or current_preference.starting_lon or UserPreferences.starting_lon.default.arg
        current_preference.starting_lat = form.starting_lat.data or current_preference.starting_lat or UserPreferences.starting_lat.default.arg
        current_preference.starting_zoom = form.starting_zoom.data or current_preference.starting_zoom or UserPreferences.starting_zoom.default.arg
        db.session.commit()

    elif request.method == 'GET':
        form.starting_lon.data = current_preference.starting_lon
        form.starting_lat.data = current_preference.starting_lat
        form.starting_zoom.select = current_preference.starting_zoom

    return render_template('account.html', title='Account', form=form)


@users.route("/register-team", methods=['GET', 'POST'])
@login_required
def new_team():
    form = TeamForm()
    if form.validate_on_submit():
        if Team.query.filter_by(name=form.name.data).first():
            abort(400)
        team = Team(name=form.name.data)
        db.session.add(team)
        db.session.commit()
        current_user.team_id = team.id
        db.session.commit()
        flash('Your Team was created', 'success')
        return redirect(url_for('users.team'))
    return render_template('new-team.html', title='Create Team', form=form, fields=['name'])


@users.route('/team')
def team():
    team = Team.query.get(current_user.team_id)
    users = User.query.filter_by(team_id=None)
    return render_template('team.html', title='Edit Team', team=team, users=users)


@users.route('/add-user-to-team', methods=['POST'])
def add_to_team():
    user_id = request.form['user']
    user = User.query.get(user_id)
    team = current_user.team_id
    user.team_id = team
    db.session.commit()
    return redirect(url_for('users.team'))
