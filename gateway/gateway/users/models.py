"""This domain module provides the database model for the user database.

This includes all required table definitions and auxiliary data structures.
"""
import enum
from datetime import datetime

from gateway import gateway

db = gateway.get_user_db()


class AuthType(enum.Enum):
    """Enum providing all types of authentication."""
    basic = 0
    oidc = 1


class Users(db.Model):
    """DB table definition for a user."""

    __tablename__ = 'users'

    id = db.Column(db.String, primary_key=True)  # noqa A003
    """Unique string identifier of a user."""
    auth_type = db.Column(db.Enum(AuthType), nullable=False)
    """The authentication type (basic / oidc) connected to this user as enum."""
    role = db.Column(db.Text, nullable=False, default='user')
    """The user's role (user / admin) as string."""
    username = db.Column(db.Text, unique=True)
    """A unique username for the user - required for basic auth."""
    password_hash = db.Column(db.Text)
    """The hashed user password as a string - required for basic auth."""
    email = db.Column(db.Text, unique=True)
    """The email address of the user - unique key - required for oidc auth."""
    identity_provider_id = db.Column(db.String, db.ForeignKey('identity_providers.id'))
    """The string id of the connected identity provider (ForeignKey) - required fir oidc auth."""
    profile_id = db.Column(db.String, db.ForeignKey('profiles.id'), nullable=False)
    """The string id of the connected profile (ForeignKey)."""
    budget = db.Column(db.Integer)
    """The user's budget (optional)."""
    name = db.Column(db.Text)
    """A human-friendly name for the user (optional)."""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    """UTC datetime of the creation of the records."""
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    """UTC datetime of the last modification of this record."""

    storage = db.relationship('Storage', uselist=False, cascade='all, delete, delete-orphan')
    """Specification about the user's connected storage :class:`~gateway.users.models.Storage`."""
    links = db.relationship('Links', cascade='all, delete, delete-orphan')
    """A list of related :class:`~gateway.users.models.Links`."""


class IdentityProviders(db.Model):
    """DB table definition for an identity provider."""

    __tablename__ = 'identity_providers'

    id = db.Column(db.String, primary_key=True)  # noqa A003
    """A unique string id of the identity provider."""
    id_openeo = db.Column(db.String, nullable=False, unique=True)
    """A unique name of the identity provider."""
    issuer_url = db.Column(db.Text, nullable=False)
    """The issuer url."""
    scopes = db.Column(db.Text, nullable=False)
    """A comma separate list of scopes."""
    title = db.Column(db.String, nullable=False, unique=True)
    """A unique title."""
    description = db.Column(db.Text)
    """A longer description (optional)."""

    links = db.relationship('Links', cascade='all, delete, delete-orphan')
    """A list of related :class:`~gateway.users.models.Links`."""


class Links(db.Model):
    """DB table definition for a link."""

    __tablename__ = 'links'

    id = db.Column(db.Integer, primary_key=True)  # noqa A003
    """A unique integer id of the link."""
    identity_provider_id = db.Column(db.String, db.ForeignKey('identity_providers.id'))
    """The id of the related identity provider (ForgeinKey - optional)."""
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    """The id of the related user (ForeignKey - optional)."""
    rel = db.Column(db.String, nullable=False)
    """Relationship between the current document and the linked document."""
    href = db.Column(db.String, nullable=False)  # should be uri!
    """A valid URL."""
    type = db.Column(db.String, nullable=True)  # noqa A003
    """A string that hints at the format used to represent data at the provided URI (optional)."""
    title = db.Column(db.String, nullable=True)
    """Used as a human-readable label for a link (optional)."""


class Profiles(db.Model):
    """DB table definition for a user profile."""

    __tablename__ = 'profiles'

    # To be extended as needed
    id = db.Column(db.String, primary_key=True)  # noqa A003
    """A unique string identifier of the profile."""
    name = db.Column(db.Text, nullable=False, unique=True)
    """A human readable name."""
    data_access = db.Column(db.Text, nullable=False)
    """A comma separate list of defined data_access levels."""


class Storage(db.Model):
    """DB table definition for storage."""

    __tablename__ = 'storage'

    id = db.Column(db.Integer, primary_key=True)  # noqa A003
    """A unique integer id of te storage."""
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    """The id of the related user (ForeignKey)."""
    free = db.Column(db.Integer, nullable=False)
    """Free storage space in bytes, which is still available to the user."""
    quota = db.Column(db.Integer, nullable=False)
    """Maximum storage space (disk quota) in bytes available to the user."""
