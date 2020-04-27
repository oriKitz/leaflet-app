from flask_login import current_user
from geoportal.models import Layer, User


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