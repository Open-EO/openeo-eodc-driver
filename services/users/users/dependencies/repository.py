"""Provide a set of database queries."""
from typing import Any, Callable, Dict, Optional

from sqlalchemy.orm import Session

from users.dependencies.utils import db_to_dict_user
from users.models import IdentityProviders, Profiles, Users


def get_identity_provider_id(db_session: Session, identity_provider_id: str = None) -> Optional[str]:
    """Get the internal id of an identity provider from its id_openeo."""
    if identity_provider_id:
        return db_session.query(IdentityProviders.id).filter_by(id_openeo=identity_provider_id).scalar()
    return None


def get_profile_id(db_session: Session, profile_name: str) -> str:
    """Get the internal profile id from its profile name."""
    return db_session.query(Profiles.id).filter(Profiles.name == profile_name).scalar()


def get_user_by_username(db_session: Session, username: str) -> Users:
    """Get the User object from its username."""
    return db_session.query(Users).filter_by(username=username).first()


def get_user_by_email(db_session: Session, email: str) -> Users:
    """Get the User from its email."""
    return db_session.query(Users).filter_by(email=email).first()


def get_user_by_id(db_session: Session, user_id: str) -> Users:
    """Get the user from its id."""
    return db_session.query(Users).filter_by(id=user_id).first()


def get_user_entity(db_session: Session, get_user: Callable, **params: Any) -> Optional[Dict[str, Any]]:
    """Get user dict using the provided query method."""
    user_entity = None
    user = get_user(db_session, **params)
    if user:
        profile = db_session.query(Profiles).filter(Profiles.id == user.profile_id).first()
        user_entity = db_to_dict_user(db_user=user, db_profile=profile)
    return user_entity


def get_user_entity_from_id(db_session: Session, user_id: str) -> Optional[Dict[str, Any]]:
    """Get the user dict from its internal id."""
    return get_user_entity(db_session, get_user_by_id, **{"user_id": user_id})


def get_user_entity_by_email(db_session: Session, email: str) -> Optional[Dict[str, Any]]:
    """Get the user dict from its email."""
    return get_user_entity(db_session, get_user_by_email, **{"email": email})


def get_user_entity_by_username(db_session: Session, username: str) -> Optional[Dict[str, Any]]:
    """Get the user dict from its email."""
    return get_user_entity(db_session, get_user_by_username, **{"username": username})
