from geoportal import db
from flask_login import UserMixin
import datetime
from geoportal import login_manager
from sqlalchemy.inspection import inspect


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=False, default='')
    last_name = db.Column(db.String(20), nullable=False, default='')
    password = db.Column(db.String(60), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    roles = db.relationship('Role', secondary='user_roles')
    layers = db.relationship('Layer', backref='user', lazy=True)
    queries = db.relationship('Query', backref='user', lazy=True)
    preferences = db.relationship('UserPreferences', backref='user', lazy=True)

    def __repr__(self):
        return f"'{self.username}', '{self.email}'"

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def has_role(self, role_name):
        for role in self.roles:
            if role.name == role_name:
                return True
        return False


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, default=0)
    query_name = db.Column(db.String(120))
    db_name = db.Column(db.String(20))
    date_uploaded = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    last_update_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    query_text = db.Column(db.Text, nullable=False, default='')
    only_user = db.Column(db.Boolean, default=False)
    only_team = db.Column(db.Boolean, default=False)
    public = db.Column(db.Boolean, default=True)
    parameters = db.relationship('QueryTextParameters', backref='query', lazy=True)
    polygon_parameters = db.relationship('QueryPolygonParameters', backref='query', lazy=True)

    def __repr__(self):
        return self.query_name

    @staticmethod
    def get_user(user_id):
        return User.query.get(user_id)

    @property
    def pretty_last_update_time(self):
        return self.last_update_time.strftime('%Y-%m-%d %H:%M')


class QueryTextParameters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey('query.id'), nullable=False)
    parameter_name = db.Column(db.String(100), nullable=False)
    parameter_type = db.Column(db.String(100), nullable=False)

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys() if c != 'query'}


class QueryPolygonParameters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey('query.id'), nullable=False)
    lon_column = db.Column(db.String(100), nullable=False)
    lat_column = db.Column(db.String(100), nullable=False)


class Layer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    default_color = db.Column(db.String(20), default='blue')
    only_user = db.Column(db.Boolean, default=True)
    only_team = db.Column(db.Boolean, default=False)
    public = db.Column(db.Boolean, default=False)
    points = db.relationship('Point', backref='layer', lazy=True)
    polygons = db.relationship('Polygon', backref='layer', lazy=True)

    def __repr__(self):
        return self.name


class Point(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    layer_id = db.Column(db.Integer, db.ForeignKey('layer.id'))
    lon = db.Column(db.Float, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, default='')
    color = db.Column(db.String(20), default='blue')

    def __repr__(self):
        return f'{self.lon}, {self.lat}: {self.description}'


class Polygon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    layer_id = db.Column(db.Integer, db.ForeignKey('layer.id'))
    coordinates = db.relationship('PolygonCoordinate', order_by='PolygonCoordinate.index', backref='layer', lazy=True)
    description = db.Column(db.Text, default='')
    color = db.Column(db.String(20), default='blue')


class PolygonCoordinate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    polygon_id = db.Column(db.Integer, db.ForeignKey('polygon.id'))
    index = db.Column(db.Integer, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    lat = db.Column(db.Float, nullable=False)


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    users = db.relationship('User', backref='team', lazy=True)


class UserMarkedQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    query_id = db.Column(db.Integer, db.ForeignKey('query.id'))


class UserMarkedLayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    layer_id = db.Column(db.Integer, db.ForeignKey('layer.id'))


class UserPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    starting_lon = db.Column(db.Float, default=37.485509)
    starting_lat = db.Column(db.Float, default=33.247876)
    starting_zoom = db.Column(db.Integer, default=6)
