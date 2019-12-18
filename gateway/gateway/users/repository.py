import os
from typing import List

from gateway.users.models import db, Users, IdentityProviders, Profiles
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from sqlalchemy import exc


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


def insert_into_db(obj):
    try:
        db.session.add(obj)
        db.session.commit()
    except exc.IntegrityError:
        db.session().rollback()


def insert_identity_provider(id_openeo: str, issuer_url: str, scopes: List[str], title: str, description: str = None):
    identity_provider = IdentityProviders(id_openeo, issuer_url, scopes, title, description)
    insert_into_db(identity_provider)


def insert_profile(name: str, data_access: List[str]):
    profile = Profiles(name, data_access)
    insert_into_db(profile)


def insert_users(auth_type: str, profile_name: str, role:str = 'user', username: str = None, password: str = None, email: str = None,
                 identity_provider: str = None):
    identity_provider_id = get_identity_provider_id(identity_provider)
    profile_id = get_profile_id(profile_name)

    user = Users(auth_type, profile_id, role, username, password, email, identity_provider_id)
    insert_into_db(user)


def get_identity_provider_id(identity_provider: str = None):
    if identity_provider:
        return db.session.query(IdentityProviders.id).filter(IdentityProviders.id_openeo == identity_provider).scalar()


def get_profile_id(profile_name: str):
    return db.session.query(Profiles.id).filter(Profiles.name == profile_name).scalar()
