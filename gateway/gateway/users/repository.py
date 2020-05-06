from typing import Optional

from gateway.users.models import db, Users, IdentityProviders, Profiles


def get_identity_provider_id(identity_provider: str = None) -> Optional[str]:
    if identity_provider:
        return db.session.query(IdentityProviders.id).filter(IdentityProviders.id_openeo == identity_provider).scalar()


def get_profile_id(profile_name: str) -> str:
    return db.session.query(Profiles.id).filter(Profiles.name == profile_name).scalar()


def get_user_by_username(username: str) -> Users:
    return db.session.query(Users).filter_by(username=username).first()


def get_user_by_email(email: str) -> Users:
    return db.session.query(Users).filter_by(email=email).first()
