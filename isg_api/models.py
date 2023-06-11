from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from sqlalchemy import event
from datetime import datetime
from isg_api.globals import login, db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {0}>'.format(self.username)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    smart_leaf_id = db.Column(db.Integer, db.ForeignKey('smart_leaf.id'))
    sensor_type_id = db.Column(db.Integer, db.ForeignKey('sensor_type.id'))
    value = db.Column(db.Float)
    measured_on = db.Column(db.DateTime, default=datetime.utcnow)


class SensorType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32), index=True, unique=True)
    unit = db.Column(db.String(32))

    data = db.relationship('sensor_data', primaryjoin=id == SensorData.sensor_type_id, backref='sensor_type', lazy='dynamic')


class SmartLeaf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plant.id'))
    box_idx = db.Column(db.Integer)
    mac_address = db.Column(db.String(64), index=True, unique=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    data = db.relationship('sensor_data', primaryjoin=id == SensorData.smart_leaf_id, backref='smart_leaf', lazy='dynamic')


class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    description_1 = db.Column(db.String(3000))
    description_2 = db.Column(db.String(3000))
    description_3 = db.Column(db.String(3000))
    water_min = db.Column(db.Float)
    water_max = db.Column(db.Float)
    light_min = db.Column(db.Float)
    light_max = db.Column(db.Float)
    harvest_begin = db.Column(db.DateTime)
    harvest_end = db.Column(db.DateTime)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    edited_on = db.Column(db.DateTime, default=datetime.utcnow)

    smart_leafs = db.relationship('smart_leaf', primaryjoin=id == SmartLeaf.plant_id, backref='plant', lazy='dynamic')


@event.listens_for(Plant, 'before_update')
def receive_before_update(mapper, connection, target):
    target.edited_on = datetime.utcnow()
