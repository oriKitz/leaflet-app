from flask import request, jsonify, abort, Blueprint, render_template
from geoportal import db
from flask_login import current_user, login_required
from geoportal.models import User, Layer, Point, UserMarkedLayer
from .utils import get_allowed_layers, get_favorite_layers, get_feature_collection_by_layer

mapping = Blueprint('mapping', __name__)


@mapping.route('/points/<int:layer_id>')
def get_layer_geojson(layer_id):
    return get_feature_collection_by_layer(layer_id)


@mapping.route('/get-all-layers')
def get_all_layers_points():
    layers = get_allowed_layers()
    return {layer.id: get_feature_collection_by_layer(layer.id) for layer in layers}


@mapping.route('/point', methods=['GET', 'POST'])
def update_point():
    lon = request.form['lon']
    lat = request.form['lat']
    description = request.form['description']
    layer_id = request.form['layer']
    if not layer_id:
        return abort(400)
    layer = Layer.query.get(layer_id)
    point = Point(layer_id=layer.id, lon=lon, lat=lat, description=description)
    db.session.add(point)
    db.session.commit()
    return jsonify({'status': 'success', 'layer_id': layer.id, 'color': layer.default_color})


@mapping.route('/layer', methods=['GET', 'POST'])
def create_layer():
    name = request.form['name']
    color = request.form['color']
    share_team = request.form['team']
    share_team = share_team == 'true'
    only_user = not share_team
    layer = Layer(name=name, user_id=current_user.id, only_user=only_user, only_team=share_team, default_color=color)
    db.session.add(layer)
    db.session.commit()
    return jsonify({'layer_id': layer.id, 'layer_name': name, 'private': not share_team, 'color': color})


@mapping.route('/edit-layer/<int:layer_id>', methods=['POST'])
def edit_layer(layer_id):
    layer_name = request.form['name']
    share_team = request.form['team']
    color = request.form['color']
    layer = Layer.query.get(layer_id)
    if color != '---':
        layer.default_color = color
    share_team = share_team == 'true'
    only_user = not share_team
    layer.name = layer_name
    layer.only_user = only_user
    layer.only_team = share_team
    db.session.commit()
    return jsonify({'status': 'success'})


@mapping.route('/layer-from-query', methods=['POST'])
def craete_layer_with_points():
    json = request.get_json()
    layer_name = json['name']
    share_team = json['team']
    points = json['layer']
    color = json['color']
    print(color)
    only_user = not share_team
    layer = Layer(name=layer_name, user_id=current_user.id, only_user=only_user, only_team=share_team, default_color=color)
    db.session.add(layer)
    db.session.commit()
    for point in points:
        p = Point(layer_id=layer.id, lon=point[0], lat=point[1], description=point[2])
        db.session.add(p)
    db.session.commit()
    return jsonify({'layer_id': layer.id, 'layer_name': layer_name, 'private': not share_team, 'color': color})


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


@mapping.route('/layers')
@login_required
def get_layers():
    layers = get_allowed_layers()
    return render_template('layers.html', layers=layers, marked_layers=get_favorite_layers())


@mapping.route('/favorite-layer', methods=['GET', 'POST'])
def toggle_favorite_query():
    layer_id = request.form['layer_id']
    user_id = current_user.id
    checkbox = request.form['checkbox'] == 'true'
    existing_instance = UserMarkedLayer.query.filter_by(layer_id=layer_id, user_id=user_id).first()
    if existing_instance:
        if checkbox:
            abort(400, 'Requesting to mark as favorite but layer already marked.')
        else:
            db.session.delete(existing_instance)
            db.session.commit()
            return jsonify({'status': 'success'})
    elif checkbox:
        marked_layer = UserMarkedLayer(layer_id=layer_id, user_id=user_id)
        db.session.add(marked_layer)
        db.session.commit()
        return jsonify({'status': 'success'})
    else:
        abort(400, 'Requesting to unmark as favorite but layer already unmarked.')


@mapping.route('/delete-layer/<int:layer_id>', methods=['POST'])
def delete_layer(layer_id):
    layer = Layer.query.get(layer_id)
    if not layer:
        abort(400, 'Layer does not exist')
    marked_layer = UserMarkedLayer.query.filter_by(user_id=current_user.id, layer_id=layer_id).first()
    if marked_layer:
        db.session.delete(marked_layer)
    points = Point.query.filter_by(layer_id=layer_id)
    for point in points:
        db.session.delete(point)
    db.session.delete(layer)
    db.session.commit()
    return jsonify({'status': 'success'})
