from flask import Flask, render_template, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_user import UserManager
from .config import Config
from flask_admin import Admin, helpers
from flask_security import Security, SQLAlchemyUserDatastore
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(__name__ + '.Config')
app.config['SECRET_KEY'] = '9ed456ae10f7eb034612afd2a46790bf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
admin = Admin(app, name='geoportal', template_mode='bootstrap3')
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from .models import User, Role, Query, QueryTextParameters, Point, Layer
# from .utils import MyModelView

# user_manager = UserManager(app, db, User)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Query, db.session))
admin.add_view(ModelView(QueryTextParameters, db.session))
admin.add_view(ModelView(Point, db.session))
admin.add_view(ModelView(Layer, db.session))
# admin.add_view(MyModelView(User, db.session))
# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security = Security(app, user_datastore)
#
# @security.context_processor
# def security_context_processor():
#     return dict(
#         admin_base_template=admin.base_template,
#         admin_view=admin.index_view,
#         h=helpers,
#         get_url=url_for
#     )

from geoportal import views