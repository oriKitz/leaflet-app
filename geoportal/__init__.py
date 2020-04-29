from flask import Flask, render_template, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from flask_admin import Admin, helpers
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from .utils import MyModelView


app = Flask(__name__)
app.config.from_object(__name__ + '.Config')
app.config['SECRET_KEY'] = '9ed456ae10f7eb034612afd2a46790bf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/site.db'
app.config['UPLOAD_FOLDER'] = r'e:\temp\uploads'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
admin = Admin(app, name='geoportal', template_mode='bootstrap3')
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

from .models import User, Role, Query, QueryTextParameters, Point, Layer, Team

admin.add_view(MyModelView(Team, db.session))
admin.add_view(MyModelView(Query, db.session))
admin.add_view(MyModelView(QueryTextParameters, db.session))
admin.add_view(MyModelView(Point, db.session))
admin.add_view(MyModelView(Layer, db.session))
admin.add_view(MyModelView(User, db.session))

from geoportal.main.views import main
from geoportal.mapping.views import mapping
from geoportal.queries.views import queries
from geoportal.users.views import users

app.register_blueprint(main)
app.register_blueprint(mapping)
app.register_blueprint(queries)
app.register_blueprint(users)
