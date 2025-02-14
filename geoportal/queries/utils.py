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


def discard_apostrophes(element):
    if (element[0] == '"' and element[-1] == '"') or (element[0] == "'" and element[-1] == "'"):
        element = element[1:-1]
    return element


def handle_parameter(param_value, param_type):
    if param_type == 'string':
        param_value = discard_apostrophes(param_value)
        return f"'{param_value}'"
    if param_type == 'number':
        return param_value
    if param_type in ['stringslist', 'stringlist']:
        values_list = param_value.split(',')
        values_list = [val.strip() for val in values_list]
        values_list = [discard_apostrophes(val) for val in values_list]
        return f'''"{'", "'.join(values_list)}"'''
    if param_type in ['numberslist', 'numberlist']:
        return param_value
    # If we got here it means we have datetime
    return f"'{param_value}'" # It's ok when using sqlite


def prepare_query_with_polygon_params(query_text, form_data, polygon_parameters):
    query_polygon_pattern = '{in-polygon-[^@]*@[^}]*}'
    polygon_param_string = re.findall(query_polygon_pattern, query_text)[0]
    lon_col = polygon_parameters.lon_column
    lat_col = polygon_parameters.lat_column
    print(form_data)
    print(polygon_param_string)
    query_text = query_text.replace(polygon_param_string, f"({lon_col} between {form_data['from-lon']} and {form_data['to-lon']} and {lat_col} between {form_data['from-lat']} and {form_data['to-lat']})")
    return query_text


def prepare_query_with_parameters(query_text, form_data, parameters):
    query_params_pattern = '{([^}]*):([^}]*)}'
    query_params = re.findall(query_params_pattern, query_text)
    query_params_dict = dict(query_params)
    for param_name, param_type in query_params_dict.items():
        param_value = form_data[param_name]
        query_text = query_text.replace('{' + f'{param_name}:{param_type}' + '}', handle_parameter(param_value, param_type))
    return query_text


def prepare_query(query_id, form_data):
    query = Query.query.get(query_id)
    query_text = query.query_text
    query_params = query.parameters
    query_polygon_params = query.polygon_parameters
    query_text = prepare_query_with_parameters(query_text, form_data, query_params)
    if query_polygon_params:
        query_text = prepare_query_with_polygon_params(query_text, form_data, query_polygon_params[0])
    print(query_text)

    return query_text


def get_geojson_from_query(query):
    return get_geojson_from_df(get_df_from_query(query))


def get_geojson_from_df(df):
    features = df.apply(get_feature_from_row, axis=1).values.tolist()
    collection = FeatureCollection(features)
    return collection


def get_df_from_query(query):
    con = sqlite3.connect('geoportal/db/places.db')
    cur = con.cursor()
    cur.execute(query)
    data = cur.fetchall()
    columns = [row[0] for row in cur.description]
    df = pd.DataFrame(columns=columns, data=data)
    return df


def get_feature_from_row(row):
    properties = {}
    for col, value in row.items():
        if col not in ['lon', 'lat', 'longitude', 'latitude']:
            properties[col] = value
    if 'longitude' in row.keys():
        return Feature(geometry=geojson.Point((row['longitude'], row['latitude'])), properties=properties)
    return Feature(geometry=geojson.Point((row['lon'], row['lat'])), properties=properties)
