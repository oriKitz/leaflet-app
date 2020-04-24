from flask import render_template, url_for, request, jsonify, redirect, flash, render_template_string
from geoportal import app, db, bcrypt
import sqlite3
from geojson import Feature, Point, FeatureCollection
import pandas as pd
from flask_user import roles_required
from flask_login import login_user, current_user, logout_user, login_required
from .forms import RegistrationForm, LoginForm, NewQuery
from .models import User, Query


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/test')
def test():
    con = sqlite3.connect('geoportal/db/places.db')
    cur = con.cursor()
    cur.execute('select longitude lon, latitude lat, start_time, location_name from google')
    data = cur.fetchall()
    columns = [row[0] for row in cur.description]
    df = pd.DataFrame(columns=columns, data=data)
    features = df.apply(get_feature_from_row, axis=1).values.tolist()
    collection = FeatureCollection(features)
    return collection


def get_feature_from_row(row):
    properties = {}
    for col, value in row.items():
        if col not in ['lon', 'lat']:
            properties[col] = value
    return Feature(geometry=Point((row['lon'], row['lat'])), properties=properties)


@app.route('/queries')
@login_required
def queries():
    all_queries = Query.query.all()
    return render_template('queries.html', queries=all_queries)


@app.route('/query/<int:query_id>')
def query(query_id):
    query = Query.query.get(query_id)
    return query.query_text


@app.route('/query', methods=['GET', 'POST'])
def new_query():
    form = NewQuery()
    if form.validate_on_submit():
        query = Query(query_name=form.query_name.data, db_name=form.db_name.data, query_text=form.query.data, user_id=current_user.id)
        db.session.add(query)
        db.session.commit()
        flash('Your query has been created!', 'success')
        return redirect(url_for('query', query_id=query.id))
    return render_template('query.html', title='New Query', form=form, fields=['query_name', 'db_name', 'query'])


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, fields=['username', 'email', 'first_name', 'last_name', 'password', 'confirm_password'])


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form, fields=['username', 'password'])


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')
