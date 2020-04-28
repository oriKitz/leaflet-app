from flask_login import current_user
from geoportal.models import Layer, User, UserMarkedLayer
from sqlalchemy import and_
from geoportal import db


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
    marked_layers = db.session.query(UserMarkedLayer.layer_id).filter_by(user_id=current_user.id).all()
    return [layer[0] for layer in marked_layers]
