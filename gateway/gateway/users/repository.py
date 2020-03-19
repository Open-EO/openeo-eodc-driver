import os
from typing import Optional

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from gateway.users.models import db, Users, IdentityProviders, Profiles


def verify_auth_token(token):
    # Verify token
    s = Serializer(os.environ.get('SECRET_KEY'))
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None, None  # valid token, but expired
    except BadSignature:
        return None, None  # invalid token

    # Verify user exists
    user = db.session.query(Users).filter(Users.id == data['id']).scalar()
    if user:
        user_id = user.id
        user_verified = True
    else:
        user_id = None
        user_verified = False

    return user_id, user_verified


def get_identity_provider_id(identity_provider: str = None) -> Optional[str]:
    if identity_provider:
        return db.session.query(IdentityProviders.id).filter(IdentityProviders.id_openeo == identity_provider).scalar()


def get_profile_id(profile_name: str) -> str:
    return db.session.query(Profiles.id).filter(Profiles.name == profile_name).scalar()


def get_user_by_username(username: str) -> Users:
    return db.session.query(Users).filter_by(username=username).first()


def get_user_by_email(email: str) -> Users:
    return db.session.query(Users).filter_by(email=email).first()
