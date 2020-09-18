import enum
from datetime import datetime

from gateway import gateway

db = gateway.get_user_db()


class AuthType(enum.Enum):
    basic = 0
    oidc = 1


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
    budget = db.Column(db.Integer)
    name = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    storage = db.relationship('Storage', uselist=False, cascade='all, delete, delete-orphan')
    links = db.relationship('Links', cascade='all, delete, delete-orphan')


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
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
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


class Storage(db.Model):
    """ Model for storage """

    __tablename__ = 'storage'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    free = db.Column(db.Integer, nullable=False)
    quota = db.Column(db.Integer, nullable=False)
