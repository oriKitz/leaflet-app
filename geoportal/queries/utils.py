from flask_login import current_user
from geoportal.models import UserMarkedQuery, Query, User
from sqlalchemy import and_
import sqlite3
import geojson
from geojson import FeatureCollection, Feature
import re
import pandas as pd


def marked_queries_first(queries):
    return sorted(queries, key=lambda query: UserMarkedQuery.query.filter(and_(UserMarkedQuery.query_id == query.id, UserMarkedQuery.user_id == current_user.id)).first() is not None, reverse=True)


def get_allowed_queries():
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
