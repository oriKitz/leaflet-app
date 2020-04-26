from flask import render_template, url_for, request, jsonify, redirect, flash, abort
from geoportal import app, db, bcrypt
import sqlite3
import geojson
from geojson import Feature, FeatureCollection
import pandas as pd
import re
from flask_login import login_user, current_user, logout_user, login_required
from .forms import RegistrationForm, LoginForm, NewQuery
from .models import User, Query, QueryTextParameters, Layer, Point, UserMarkedQuery
import datetime
from sqlalchemy import and_
from time import sleep


def marked_queries_first(queries):
    return sorted(queries, key=lambda query: UserMarkedQuery.query.filter(and_(UserMarkedQuery.query_id == query.id, UserMarkedQuery.user_id == current_user.id)).first() is not None, reverse=True)


def get_allowd_queries():
    if current_user.is_authenticated:
        queries = Query.query.order_by(Query.only_user.desc(), Query.public).all()
        authorized_queries = []
        for query in queries:
            if query.public or (query.only_team and User.query.get(query.user_id).team_id == current_user.team_id) or query.user_id == current_user.id:
                authorized_queries.append(query)
        queries = authorized_queries
        queries = marked_queries_first(queries)
    else:
        queries = Query.query.filter_by(public=True).all()

    return queries


def get_allowed_layers():
    if current_user.is_authenticated:
        layers = Layer.query.all()
        authorized_layers = []
        for layer in layers:
            if (layer.only_team and User.query.get(layer.user_id).team_id == current_user.team_id) or layer.user_id == current_user.id:
                authorized_layers.append(layer)
        layers = authorized_layers
    else:
        layers = []

    return layers


@app.route('/')
@app.route('/home')
def home():
    queries = get_allowd_queries()
    layers = get_allowed_layers()
    return render_template('home.html', queries=queries, layers=layers)


@app.route('/invoke/<int:query_id>/<string:token>', methods=['GET', 'POST'])
def invoke_query(query_id, token):
    query_text = prepare_query(query_id, request.form)
    return {'geojson': get_geojson_from_query(query_text), 'token': token}


@app.route('/table_results/<int:query_id>', methods=['GET', 'POST'])
def query_table_results(query_id):
    query_text = prepare_query(query_id, request.form)
    con = sqlite3.connect('geoportal/db/places.db')
    cur = con.cursor()
    cur.execute(query_text)
    data = cur.fetchall()
    columns = [row[0] for row in cur.description]
    df = pd.DataFrame(columns=columns, data=data)
    return df.to_html(index=None, classes=['table', 'table-bordered', 'table-hover', 'table-condensed'], justify='center', table_id='full-results')


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
        return Feature(geometry=geojson.Point((row['longitude'], row['latitude'])), properties=properties)
    return Feature(geometry=geojson.Point((row['lon'], row['lat'])), properties=properties)


@app.route('/points/<int:layer_id>')
def get_layer_geojson(layer_id):
    points = Point.query.filter_by(layer_id=layer_id).all()
    features = []
    for point in points:
        features.append(Feature(geometry=geojson.Point((point.lon, point.lat)), properties={'description': point.description}))
    return FeatureCollection(features)


@app.route('/point', methods=['GET', 'POST'])
def update_point():
    lon = request.form['lon']
    lat = request.form['lat']
    description = request.form['description']
    layer = request.form['layer']
    layer_name = layer[:layer.rfind(',')]
    layer_username = layer[layer.rfind(',') + 2:]
    user = User.query.filter_by(username=layer_username).first()
    layer = Layer.query.filter_by(name=layer_name).filter_by(user_id=user.id).first()
    point = Point(layer_id=layer.id, lon=lon, lat=lat, description=description)
    db.session.add(point)
    db.session.commit()
    return jsonify({'status': 'success', 'layer_id': layer.id})


@app.route('/layer', methods=['GET', 'POST'])
def create_layer():
    name = request.form['name']
    share_team = request.form['team']
    share_team = share_team == 'true'
    only_user = not share_team
    layer = Layer(name=name, user_id=current_user.id, only_user=only_user, only_team=share_team)
    db.session.add(layer)
    db.session.commit()
    return jsonify({'status': 'success'})


@app.route('/remove-point/<int:layer_id>/<float:lon>/<float:lat>', methods=['POST'])
def remove_point(layer_id, lon, lat):
    # point = Point.query.filter(Point.layer_id == layer_id, round(Point.lon, 6) == lon, round(Point.lat, 6) == lat).first()
    layer_points = Point.query.filter_by(layer_id=layer_id)
    mathing_point = None
    for point in layer_points:
        if round(point.lon, 6) == lon and round(point.lat, 6) == lat:
            mathing_point = point
            break
    if mathing_point:
        db.session.delete(mathing_point)
        db.session.commit()
        return jsonify({'status': 'success'})
    else:
        abort(400, "Point doesn't exist")


@app.route('/favorite', methods=['GET', 'POST'])
def toggle_favorite_query():
    query_id = request.form['query_id']
    user_id = current_user.id
    checkbox = request.form['checkbox'] == 'true'
    existing_instance = UserMarkedQuery.query.filter_by(query_id=query_id, user_id=user_id).first()
    if existing_instance:
        if checkbox:
            abort(400, 'Requesting to mark as favorite but query already marked.')
        else:
            db.session.delete(existing_instance)
            db.session.commit()
            return jsonify({'status': 'success'})
    elif checkbox:
        marked_query = UserMarkedQuery(query_id=query_id, user_id=user_id)
        db.session.add(marked_query)
        db.session.commit()
        return jsonify({'status': 'success'})
    else:
        abort(400, 'Requesting to unmark as favorite but query already unmarked.')


@app.route('/queries')
@login_required
def queries():
    queries = get_allowd_queries()
    marked_queries = db.session.query(UserMarkedQuery.query_id).filter_by(user_id=current_user.id).all()
    marked_queries = [query[0] for query in marked_queries]
    return render_template('queries.html', queries=queries, marked_queries=marked_queries)


@app.route('/run_query/<string:token>', methods=['POST'])
def run_query(token):
    query = request.form['query']
    return {'geojson': get_geojson_from_query(query), 'token': token}


@app.route('/query/<int:query_id>', methods=['GET', 'POST'])
def query(query_id):
    form = NewQuery()
    query = Query.query.get(query_id)

    if form.validate_on_submit():
        query.only_team = form.only_team.data
        query.only_user = form.only_me.data
        query.public = (not query.only_team) and (not query.only_user)

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
        return jsonify({'status': 'success'})

    elif request.method == 'GET':
        form.query_name.data = query.query_name
        form.db_name.data = query.db_name
        form.query.data = query.query_text
        form.only_team.data = query.only_team
        form.only_me.data = query.only_user

    return render_template('query.html', title='Edit Query', form=form, fields=['query_name', 'db_name', 'query'], form_title='Edit Query', query_text=query.query_text)


@app.route('/query', methods=['GET', 'POST'])
def new_query():
    form = NewQuery()
    if form.validate_on_submit():
        only_team = form.only_team.data
        only_user = form.only_me.data
        public = (not only_team) and (not only_user)
        query = Query(query_name=form.query_name.data, db_name=form.db_name.data, query_text=form.query.data, user_id=current_user.id, only_user=only_user, only_team=only_team, public=public)
        db.session.add(query)
        db.session.commit()

        query_params_pattern = '{([^}]*):([^}]*)}'
        query_params = re.findall(query_params_pattern, form.query.data)
        for param in query_params:
            query_parameter = QueryTextParameters(query_id=query.id, parameter_name=param[0], parameter_type=param[1])
            db.session.add(query_parameter)

        db.session.commit()
        flash('Your query has been created!', 'success')
        return jsonify({'query_id': query.id})
        # return redirect(url_for('query', query_id=query.id))
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
