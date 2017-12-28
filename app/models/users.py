from datetime import datetime
import random
import enum

from flask import g, current_app as app
from itsdangerous import (BadSignature,
                          SignatureExpired,
                          TimedJSONWebSignatureSerializer,)
from passlib.apps import custom_app_context

from app import auth, db


@auth.verify_password
def verify_password(userid_or_token, password):

    if (type(userid_or_token) != long) and (type(userid_or_token) != int):
        user = User.verify_auth_token(userid_or_token)
        if not user:
            return False
    else:
        user = User.query.filter_by(user_id=userid_or_token).first()
        if not user or not user.verify_password(password):
            return False

    g.user = user
    return True


class StatusEnum(enum.Enum):
    enabled = 'enabled'
    disabled = 'disabled'
    blocked = 'blocked'
    pending = 'pending'


class AccountTypeEnum(enum.Enum):
    driver = 'driver'
    user = 'user'
    admin = 'admin'


class User(db.Model):
    """User Model
    """
    __tablename__ = 'User'

    user_id = db.Column(db.Integer, primary_key=True)  # auto incrementing pk
    email = db.Column(db.String(128), unique=True)
    account_type = db.Column(db.Enum(AccountTypeEnum), nullable=True)
    password = db.Column(db.String(128))
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    status = db.Column(db.Enum(StatusEnum), default=StatusEnum.enabled)
    created = db.Column(db.DateTime())
    updated = db.Column(db.DateTime(), onupdate=datetime.now)
    registration_code = db.Column(db.Integer)
    registration_confirmed = db.Column(db.Boolean)

    @staticmethod
    def hash_password(password):
        return custom_app_context.encrypt(password)

    def verify_password(self, password):
        return custom_app_context.verify(password, self.password)

    def generate_auth_token(self, expiration=600):
        signature = TimedJSONWebSignatureSerializer(
            app.config['SECRET_KEY'],
            expires_in=expiration
        )
        return signature.dumps({'userId': self.user_id})

    @staticmethod
    def verify_auth_token(token):
        signature = TimedJSONWebSignatureSerializer(app.config['SECRET_KEY'])
        try:
            data = signature.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None

        user = db.session.query(User).get(data['userId'])

        return user

    @property
    def serialize(self):
        return {
            '_id': self.user_id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
            'status': self.status.value if self.status is not None else self.status,
            'accountType': self.account_type.value if self.account_type is not None else self.account_type,
            'created': self.created,
            'updated': self.updated
        }

    @classmethod
    def get_user(cls, user_id):

        return db.session.query(cls).filter_by(user_id=user_id).first()

    def __init__(self, first_name, last_name, password, email, account_type):
        self.first_name = first_name
        self.last_name = last_name
        self.password = User.hash_password(password)
        self.email = email
        self.account_type = account_type
        self.created = datetime.now()
        self.registration_code = random.randint(10000, 99999)
        self.registration_confirmed = False
