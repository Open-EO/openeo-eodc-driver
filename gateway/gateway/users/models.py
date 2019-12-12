import enum
import os
from datetime import datetime
from typing import List
from uuid import uuid4

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer)
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
    username = db.Column(db.Text)
    password_hash = db.Column(db.Text)
    email = db.Column(db.Text)
    identity_provider_id = db.Column(db.Integer, db.ForeignKey('identity_providers.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, auth_type: str, username: str = None, password: str = None, email: str = None,
                 identity_provider_id: str = None):
        self.id = 'us-' + str(uuid4())
        self.auth_type = AUTH_TYPE_MAPPER[auth_type]
        self.username = username
        self.hash_password(password)
        self.email = email
        self.identity_provider_id = identity_provider_id

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(os.environ.get('SECRET_KEY'), expires_in=expiration)
        return s.dumps({
            'id': self.id,
        }).decode('utf-8')


class IdentityProviders(db.Model):
    """ Base model for an identity provider """

    __tablename__ = 'identity_providers'

    id = db.Column(db.Integer, primary_key=True)
    issuer_url = db.Column(db.Text, nullable=False)
    scopes = db.Column(db.Text, nullable=False)
    title = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.Text)

    def __init__(self, issuer_url: str, scopes: List[str], title: str, description: str = None):
        self.issuer_url = issuer_url
        self.scopes = ','.join(scopes)
        self.title = title
        self.description = description
