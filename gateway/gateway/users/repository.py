"""Provide a set of database queries."""
from typing import Any, Dict, Optional

from .models import IdentityProviders, Profiles, Users, db
from .utils import db_to_dict_user


def get_identity_provider_id(identity_provider: str = None) -> Optional[str]:
    """Get the internal id of an identity provider from its id_openeo."""
    if identity_provider:
        return db.session.query(IdentityProviders.id).filter(IdentityProviders.id_openeo == identity_provider).scalar()
    return None


def get_profile_id(profile_name: str) -> str:
    """Get the internal profile id from its profile name."""
    return db.session.query(Profiles.id).filter(Profiles.name == profile_name).scalar()


def get_user_by_username(username: str) -> Users:
    """Get the User object from its username."""
    return db.session.query(Users).filter_by(username=username).first()


def get_user_by_email(email: str) -> Users:
    """Get the User from its email."""
    return db.session.query(Users).filter_by(email=email).first()


def get_user_entity_from_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get the user dict from its internal id."""
    user_entity = None
    user = db.session.query(Users).filter(Users.id == user_id).scalar()
    if user:
        profile = db.session.query(Profiles).filter(Profiles.id == user.profile_id).first()
        user_entity = db_to_dict_user(db_user=user, db_profile=profile)
    return user_entity


def get_user_entity_from_email(email: str) -> Optional[Dict[str, Any]]:
    """Get the user dict from its email."""
    user_entity = None
    user = db.session.query(Users).filter(Users.email == email).scalar()
    if user:
        profile = db.session.query(Profiles).filter(Profiles.id == user.profile_id).first()
        user_entity = db_to_dict_user(db_user=user, db_profile=profile)
    return user_entity
