from flask import render_template, Blueprint
from geoportal.queries.utils import get_allowed_queries
from geoportal.mapping.utils import get_allowed_layers

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    return render_template('home.html', queries=get_allowed_queries(), layers=get_allowed_layers())
