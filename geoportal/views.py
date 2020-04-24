from flask import render_template, url_for, request, jsonify, redirect, flash, render_template_string
from geoportal import app, db, bcrypt
import sqlite3
from geojson import Feature, Point, FeatureCollection
import pandas as pd
import re
from flask_login import login_user, current_user, logout_user, login_required
from .forms import RegistrationForm, LoginForm, NewQuery
from .models import User, Query, QueryTextParameters
import datetime


@app.route('/')
@app.route('/home')
def home():
    queries = Query.query.all()
    return render_template('home.html', queries=queries)


@app.route('/revoke/<int:query_id>', methods=['GET', 'POST'])
def revoke_query(query_id):
    query_text = prepare_query(query_id, request.form)
    return get_geojson_from_query(query_text)


@app.route('/get_query_parameters/<int:query_id>')
def query_parameters(query_id):
    return jsonify([param.serialize() for param in Query.query.get(query_id).parameters])


def handle_parameter(param_value, param_type):
    if param_type == 'string':
        return f"'{param_value}'"
    if param_type == 'number':
        return param_value
    # If we got here it means we have datetime
    return f"'{param_value}'" # It's ok when using sqlite


def prepare_query(query_id, parameters_dict):
    query = Query.query.get(query_id)
    query_text = query.query_text
    query_params_pattern = '{([^}]*):([^}]*)}'
    query_params = re.findall(query_params_pattern, query_text)
    query_params_dict = dict(query_params)
    for param_name, param_value in parameters_dict.items():
        param_type = query_params_dict[param_name]
        query_text = query_text.replace('{' + f'{param_name}:{param_type}' + '}', handle_parameter(param_value, param_type))
    return query_text


def get_geojson_from_query(query):
    con = sqlite3.connect('geoportal/db/places.db')
    cur = con.cursor()
    cur.execute(query)
    data = cur.fetchall()
    columns = [row[0] for row in cur.description]
    df = pd.DataFrame(columns=columns, data=data)
    features = df.apply(get_feature_from_row, axis=1).values.tolist()
    collection = FeatureCollection(features)
    return collection


def get_feature_from_row(row):
    properties = {}
    for col, value in row.items():
        if col not in ['lon', 'lat', 'longitude', 'latitude']:
            properties[col] = value
    if 'longitude' in row.keys():
        return Feature(geometry=Point((row['longitude'], row['latitude'])), properties=properties)
    return Feature(geometry=Point((row['lon'], row['lat'])), properties=properties)


@app.route('/queries')
@login_required
def queries():
    all_queries = Query.query.all()
    return render_template('queries.html', queries=all_queries)


@app.route('/query/<int:query_id>', methods=['GET', 'POST'])
def query(query_id):
    form = NewQuery()
    query = Query.query.get(query_id)

    if form.validate_on_submit():
        old_query = query.query_text
        query.query_name = form.query_name.data
        query.db_name = form.db_name.data
        query.query_text = form.query.data
        query.last_update_time = datetime.datetime.now()
        db.session.commit()

        if form.query.data != old_query:
            params = query.parameters
            for param in params:
                db.session.delete(param)
            db.session.commit()
            query_params_pattern = '{([^}]*):([^}]*)}'
            query_params = re.findall(query_params_pattern, form.query.data)
            for param in query_params:
                query_parameter = QueryTextParameters(query_id=query.id, parameter_name=param[0], parameter_type=param[1])
                db.session.add(query_parameter)
            db.session.commit()

        flash('Your query has been updated!', 'success')
        return redirect(url_for('query', query_id=query.id))

    elif request.method == 'GET':
        form.query_name.data = query.query_name
        form.db_name.data = query.db_name
        form.query.data = query.query_text

    return render_template('query.html', title='Edit Query', form=form, fields=['query_name', 'db_name', 'query'], form_title='Edit Query', query_text=query.query_text)


@app.route('/query', methods=['GET', 'POST'])
def new_query():
    form = NewQuery()
    if form.validate_on_submit():
        query = Query(query_name=form.query_name.data, db_name=form.db_name.data, query_text=form.query.data, user_id=current_user.id)
        db.session.add(query)
        db.session.commit()

        query_params_pattern = '{([^}]*):([^}]*)}'
        query_params = re.findall(query_params_pattern, form.query.data)
        for param in query_params:
            query_parameter = QueryTextParameters(query_id=query.id, parameter_name=param[0], parameter_type=param[1])
            db.session.add(query_parameter)

        db.session.commit()
        flash('Your query has been created!', 'success')
        return redirect(url_for('query', query_id=query.id))
    return render_template('query.html', title='New Query', form=form, fields=['query_name', 'db_name', 'query'], form_title='Create New Query')


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
