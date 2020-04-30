from flask_login import current_user
from geoportal.models import Layer, User, UserMarkedLayer, Point, QueryTextParameters
from sqlalchemy import and_
from geoportal import db
from flask_login import current_user
import geojson
from geojson import Feature, FeatureCollection


def marked_layers_first(layers):
    return sorted(layers, key=lambda layer: UserMarkedLayer.query.filter(and_(UserMarkedLayer.layer_id == layer.id, UserMarkedLayer.user_id == current_user.id)).first() is not None, reverse=True)


def get_allowed_layers():
    if current_user.is_authenticated:
        layers = Layer.query.all()
        authorized_layers = []
        for layer in layers:
            if (layer.only_team and User.query.get(layer.user_id).team_id == current_user.team_id) or layer.user_id == current_user.id:
                authorized_layers.append(layer)
        layers = authorized_layers
        layers = marked_layers_first(layers)
    else:
        layers = []

    return layers


def get_favorite_layers():
    if current_user.is_authenticated:
        marked_layers = db.session.query(UserMarkedLayer.layer_id).filter_by(user_id=current_user.id).all()
        return [layer[0] for layer in marked_layers]
    return []


def get_feature_collection_by_layer(layer_id):
    points = Point.query.filter_by(layer_id=layer_id).all()
    features = []
    for point in points:
        features.append(
            Feature(geometry=geojson.Point((point.lon, point.lat)), properties={'description': point.description}))
    return FeatureCollection(features)
