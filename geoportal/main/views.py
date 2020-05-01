from flask import render_template, Blueprint
from geoportal.queries.utils import get_allowed_queries
from geoportal.mapping.utils import get_allowed_layers, get_favorite_layers
from flask_login import current_user

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    if current_user.is_authenticated:
        return render_template('home.html', queries=get_allowed_queries(), layers=get_allowed_layers(), favorite_layers=get_favorite_layers(), preferences=current_user.preferences[0])
    return render_template('home.html', queries=get_allowed_queries(), layers=get_allowed_layers(), favorite_layers=get_favorite_layers())
