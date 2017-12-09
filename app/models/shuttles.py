import enum
from datetime import datetime

from app import db


class ShuttleSizeEnum(enum.Enum):
    small = 'small'
    medium = 'medium'
    full = 'full'


class StatusEnum(enum.Enum):
    enabled = 'enabled'
    disabled = 'disabled'
    blocked = 'blocked'


class LocationTypeEnum(enum.Enum):
    bus_stop = 'bus_stop'
    building = 'building'


class Shuttle(db.Model):
    """
    Shuttle Model
    """
    __tablename__ = 'shuttle'

    id = db.Column(db.Integer, primary_key=True)  # auto incrementing pk
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    en_route = db.Column(db.Boolean, default=False)
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    size = db.Column(db.Enum(ShuttleSizeEnum))
    brand = db.Column(db.String(128))
    ac = db.Column(db.Boolean)
    no_of_seats = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Enum(StatusEnum), default=StatusEnum.enabled)
    created = db.Column(db.DateTime())
    updated = db.Column(db.DateTime(), onupdate=datetime.now)

    @classmethod
    def get_shuttle_by_id(cls, shuttle_id):
        return db.session.query(cls).filter_by(id=shuttle_id, status=StatusEnum.enabled).first()

    @property
    def serialize(self):
        return {
            'shuttle_id': self.id,
            'brand': self.brand,
            'user_id': self.user_id,
            'size': self.size.value,
            'ac': self.ac,
            'en_route': self.en_route,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'no_of_seats': self.no_of_seats,
            'status': self.status.value,
            'created': self.created,
            'updated': self.updated
        }

    def __init__(self, user_id, size, brand, ac, no_of_seats):
        self.user_id = user_id
        self.size = size
        self.brand = brand
        self.ac = ac
        self.no_of_seats = no_of_seats
        self.created = datetime.now()


class Location(db.Model):

    __tablename__ = 'location'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    type = db.Column(db.Enum(LocationTypeEnum))
    description = db.Column(db.String(128), nullable=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    status = db.Column(db.Enum(StatusEnum), default=StatusEnum.enabled)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime, onupdate=datetime.now)

    @property
    def serialize(self):
        return {
            '_id': self.id,
            'name': self.name,
            'description': self.description,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'type': self.type.value,
            'created': self.created,
            'updated': self.updated
        }

    def __init__(self, name, location_type, description, latitude, longitude):
        self.name = name
        self.type = location_type
        self.description = description
        self.latitude = latitude
        self.longitude = longitude
        self.created = datetime.now()

