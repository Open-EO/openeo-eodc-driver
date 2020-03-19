import enum
import os
from datetime import datetime
from typing import List
from uuid import uuid4

from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer)
from passlib.apps import custom_app_context as pwd_context

from gateway import gateway

db = gateway.get_user_db()


class AuthType(enum.Enum):
    basic = 0
    oidc = 1


AUTH_TYPE_MAPPER = {
    "basic": AuthType.basic,
    "oidc": AuthType.oidc
}


class Users(db.Model):
    """ Base model for a user. """

    __tablename__ = 'users'

    id = db.Column(db.String, primary_key=True)
    auth_type = db.Column(db.Enum(AuthType), nullable=False)
    role = db.Column(db.Text, nullable=False, default='user')
    username = db.Column(db.Text, unique=True)
    password_hash = db.Column(db.Text)
    email = db.Column(db.Text, unique=True)
    identity_provider_id = db.Column(db.String, db.ForeignKey('identity_providers.id'))
    profile_id = db.Column(db.String, db.ForeignKey('profiles.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, auth_type: str, profile_id: str, role: str, username: str = None, password: str = None, email: str = None,
                 identity_provider_id: str = None):
        self.id = 'us-' + str(uuid4())
        self.auth_type = AUTH_TYPE_MAPPER[auth_type]
        self.profile_id = profile_id
        self.role = role
        self.username = username
        self.hash_password(password)
        self.email = email
        self.identity_provider_id = identity_provider_id

    def hash_password(self, password):
        if password:
            self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        serialized = Serializer(os.environ.get('SECRET_KEY'), expires_in=expiration)
        token = serialized.dumps({'id': self.id}).decode('utf-8')
        
        return self.id, token


class IdentityProviders(db.Model):
    """ Base model for an identity provider """

    __tablename__ = 'identity_providers'

    id = db.Column(db.String, primary_key=True)
    id_openeo = db.Column(db.String, nullable=False, unique=True)
    issuer_url = db.Column(db.Text, nullable=False)
    scopes = db.Column(db.Text, nullable=False)
    title = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.Text)

    links = db.relationship('Links', cascade='all, delete, delete-orphan')


class Links(db.Model):

    __tablename__ = 'links'

    id = db.Column(db.Integer, primary_key=True)
    identity_provider_id = db.Column(db.String, db.ForeignKey('identity_providers.id'))
    rel = db.Column(db.String, nullable=False)
    href = db.Column(db.String, nullable=False)  # should be uri!
    type = db.Column(db.String, nullable=True)
    title = db.Column(db.String, nullable=True)


class Profiles(db.Model):
    """ Base model for a user profile """

    __tablename__ = 'profiles'

    # To be extended as needed
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    data_access = db.Column(db.Text, nullable=False)

    def __init__(self, name: str, data_access: str):
        self.id = 'pr-' + str(uuid4())
        self.name = name
        self.data_access = data_access
