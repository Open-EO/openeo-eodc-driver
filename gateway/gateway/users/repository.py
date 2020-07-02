from typing import Optional, Any, Dict

from .models import db, Users, IdentityProviders, Profiles
from .utils import db_to_dict_user


def get_identity_provider_id(identity_provider: str = None) -> Optional[str]:
    if identity_provider:
        return db.session.query(IdentityProviders.id).filter(IdentityProviders.id_openeo == identity_provider).scalar()


def get_profile_id(profile_name: str) -> str:
    return db.session.query(Profiles.id).filter(Profiles.name == profile_name).scalar()


def get_user_by_username(username: str) -> Users:
    return db.session.query(Users).filter_by(username=username).first()


def get_user_by_email(email: str) -> Users:
    return db.session.query(Users).filter_by(email=email).first()


def get_user_entity_from_id(user_id: str) -> Optional[Dict[str, Any]]:
    user_entity = None
    user = db.session.query(Users).filter(Users.id == user_id).scalar()
    if user:
        profile = db.session.query(Profiles).filter(Profiles.id == user.profile_id).first()
        user_entity = db_to_dict_user(db_user=user, db_profile=profile)
    return user_entity


def get_user_entity_from_email(email: str) -> Optional[Dict[str, Any]]:
    user_entity = None
    user = db.session.query(Users).filter(Users.email == email).scalar()
    if user:
        profile = db.session.query(Profiles).filter(Profiles.id == user.profile_id).first()
        user_entity = db_to_dict_user(db_user=user, db_profile=profile)
    return user_entity
