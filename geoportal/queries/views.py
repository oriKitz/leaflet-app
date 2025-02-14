from flask import render_template, request, jsonify, flash, abort, Blueprint
from geoportal import db, app
from .forms import NewQuery
from geoportal.models import Query, QueryTextParameters, UserMarkedQuery, QueryPolygonParameters
import datetime
from .utils import *
from flask_login import login_required
import os
from werkzeug.utils import secure_filename
import pandas as pd

queries = Blueprint('queries', __name__)


@queries.route('/invoke/<int:query_id>/<string:token>', methods=['GET', 'POST'])
def invoke_query(query_id, token):
    query_text = prepare_query(query_id, request.form)
    try:
        query_results = get_geojson_from_query(query_text)
        return {'geojson': query_results, 'token': token, 'results_amount': len(query_results['features']), 'query_name': Query.query.get(query_id).query_name}
    except Exception as e:
        return jsonify(error_type=str(type(e)), error_message=str(e), query_name=Query.query.get(query_id).query_name, params=dict(request.form), token=token), 500


@queries.route('/run_query/<string:token>', methods=['POST'])
def run_query(token):
    query = request.form['query']
    try:
        query_results = get_geojson_from_query(query)
        return {'geojson': query_results, 'token': token, 'results_amount': len(query_results['features'])}
    except Exception as e:
        return jsonify(error_type=str(type(e)), error_message=str(e), token=token), 500


@queries.route('/table_results/<int:query_id>', methods=['GET', 'POST'])
def query_table_results(query_id):
    query_text = prepare_query(query_id, request.form)
    con = sqlite3.connect('geoportal/db/places.db')
    cur = con.cursor()
    cur.execute(query_text)
    data = cur.fetchall()
    columns = [row[0] for row in cur.description]
    df = pd.DataFrame(columns=columns, data=data)
    return df.to_html(index=None, classes=['table', 'table-bordered', 'table-hover', 'table-condensed'], justify='center', table_id='full-results')


@queries.route('/get_query_parameters/<int:query_id>')
def query_parameters(query_id):
    return jsonify([param.serialize() for param in Query.query.get(query_id).parameters])


@queries.route('/get-all-queries-params')
def get_all_queries_parameters():
    queries = get_allowed_queries()
    return {query.id: [param.serialize() for param in Query.query.get(query.id).parameters] for query in queries}


@queries.route('/get-all-queries-polygon-params')
def get_all_queries_poly_params():
    queries = get_allowed_queries()
    return {query.id: [query.polygon_parameters[0].lon_column, query.polygon_parameters[0].lat_column] for query in queries if query.polygon_parameters}


@queries.route('/favorite', methods=['GET', 'POST'])
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


@queries.route('/queries')
@login_required
def get_queries():
    queries = get_allowed_queries()
    marked_queries = db.session.query(UserMarkedQuery.query_id).filter_by(user_id=current_user.id).all()
    marked_queries = [query[0] for query in marked_queries]
    return render_template('queries.html', queries=queries, marked_queries=marked_queries)


@queries.route('/query/<int:query_id>', methods=['GET', 'POST'])
@login_required
def query(query_id):
    query = Query.query.get(query_id)

    if (query.user_id != current_user.id and query.only_user) or \
        (query.only_team and User.query.get(query.user_id).team_id != current_user.team_id):
        return abort(403)

    form = NewQuery()
    if form.validate_on_submit():
        query.only_team = form.only_team.data
        query.only_user = form.only_me.data
        query.public = (not query.only_team) and (not query.only_user)

        old_query = query.query_text
        query.query_name = form.query_name.data
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

            if query.polygon_parameters:
                db.session.delete(query.polygon_parameters[0])
                db.session.commit()
            query_polygon_pattern = '{in-polygon-([^@]*)@([^}]*)}'
            polygon_limits = re.findall(query_polygon_pattern, form.query.data)
            if polygon_limits:
                polygon_limit = polygon_limits[0]
                poly = QueryPolygonParameters(query_id=query.id, lon_column=polygon_limit[0], lat_column=polygon_limit[1])
                db.session.add(poly)
            db.session.commit()

        flash('Your query has been updated!', 'success')
        return jsonify({'status': 'success'})

    elif request.method == 'GET':
        form.query_name.data = query.query_name
        form.query.data = query.query_text
        form.only_team.data = query.only_team
        form.only_me.data = query.only_user

    return render_template('query.html', title='Edit Query', form=form, fields=['query_name', 'query'], form_title='Edit Query', query_text=query.query_text)


@queries.route('/query', methods=['GET', 'POST'])
@login_required
def new_query():
    form = NewQuery()
    if form.validate_on_submit():
        only_team = form.only_team.data
        only_user = form.only_me.data
        public = (not only_team) and (not only_user)
        query = Query(query_name=form.query_name.data, query_text=form.query.data, user_id=current_user.id, only_user=only_user, only_team=only_team, public=public)
        db.session.add(query)
        db.session.commit()

        query_params_pattern = '{([^}]*):([^}]*)}'
        query_params = re.findall(query_params_pattern, form.query.data)
        for param in query_params:
            query_parameter = QueryTextParameters(query_id=query.id, parameter_name=param[0], parameter_type=param[1])
            db.session.add(query_parameter)

        query_polygon_pattern = '{in-polygon-([^@]*)@([^}]*)}'
        polygon_limits = re.findall(query_polygon_pattern, form.query.data)
        if polygon_limits:
            polygon_limit = polygon_limits[0]
            poly = QueryPolygonParameters(query_id=query.id, lon_column=polygon_limit[0], lat_column=polygon_limit[1])
            db.session.add(poly)

        db.session.commit()
        flash('Your query has been created!', 'success')
        return jsonify({'query_id': query.id})
        # return redirect(url_for('query', query_id=query.id))
    return render_template('query.html', title='New Query', form=form, fields=['query_name', 'query'], form_title='Create New Query')


@queries.route('/upload-file', methods=['POST'])
def upload_file():
    file = request.files['file']
    extension = file.filename[file.filename.rfind('.') + 1:]
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    if extension == 'csv':
        df = pd.read_csv(file_path)
    elif extension == 'xlsx':
        df = pd.read_excel(file_path)
    else:
        df = None
    geojson_res = get_geojson_from_df(df)
    os.remove(file_path)
    return {'geojson': geojson_res, 'results_amount': len(geojson_res['features']), 'filename': file.filename}


@queries.route('/delete-query/<int:query_id>', methods=['POST'])
def delete_query(query_id):
    q = Query.query.get(query_id)
    marked_query = UserMarkedQuery.query.filter_by(user_id=current_user.id, query_id=query_id).first()
    if marked_query:
        db.session.delete(marked_query)
    query_params = q.parameters
    for param in query_params:
        db.session.delete(param)
    db.session.delete(q)
    db.session.commit()
    return jsonify({'status': 'success'})
