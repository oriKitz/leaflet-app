from flask import request, jsonify, abort, Blueprint
from geoportal import db
import geojson
from geojson import Feature, FeatureCollection
from flask_login import current_user
from geoportal.models import User, Layer, Point

mapping = Blueprint('mapping', __name__)


@mapping.route('/points/<int:layer_id>')
def get_layer_geojson(layer_id):
    points = Point.query.filter_by(layer_id=layer_id).all()
    features = []
    for point in points:
        features.append(Feature(geometry=geojson.Point((point.lon, point.lat)), properties={'description': point.description}))
    return FeatureCollection(features)


@mapping.route('/point', methods=['GET', 'POST'])
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


@mapping.route('/layer', methods=['GET', 'POST'])
def create_layer():
    name = request.form['name']
    share_team = request.form['team']
    share_team = share_team == 'true'
    only_user = not share_team
    layer = Layer(name=name, user_id=current_user.id, only_user=only_user, only_team=share_team)
    db.session.add(layer)
    db.session.commit()
    return jsonify({'status': 'success'})


@mapping.route('/layer-query', methods=['POST'])
def craete_layer_with_points():
    json = request.get_json()
    layer_name = json['name']
    share_team = json['team']
    points = json['layer']
    only_user = not share_team
    layer = Layer(name=layer_name, user_id=current_user.id, only_user=only_user, only_team=share_team)
    db.session.add(layer)
    db.session.commit()
    for point in points:
        p = Point(layer_id=layer.id, lon=point[0], lat=point[1], description=point[2])
        db.session.add(p)
    db.session.commit()
    return jsonify({'status': 'success'})


@mapping.route('/remove-point/<int:layer_id>/<float:lon>/<float:lat>', methods=['POST'])
def remove_point(layer_id, lon, lat):
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
