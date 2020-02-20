import os
from typing import List, Tuple, Optional

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from sqlalchemy import exc

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


def insert_into_db(obj) -> Tuple[bool, Optional[Exception]]:
    try:
        db.session.add(obj)
        db.session.commit()
        return True, None
    except exc.IntegrityError as e:
        db.session().rollback()
        return False, e


def insert_identity_provider(id_openeo: str, issuer_url: str, scopes: List[str], title: str, description: str = None) -> Tuple[bool, Optional[Exception]]:
    identity_provider = IdentityProviders(id_openeo, issuer_url, scopes, title, description)
    return insert_into_db(identity_provider)


def insert_profile(name: str, data_access: str) -> Tuple[bool, Optional[Exception]]:
    profile = Profiles(name, data_access)
    return insert_into_db(profile)


def insert_users(auth_type: str, profile_name: str, role: str = 'user', username: str = None, password: str = None,
                 email: str = None, identity_provider: str = None) -> Tuple[bool, Optional[Exception]]:
    identity_provider_id = get_identity_provider_id(identity_provider)
    profile_id = get_profile_id(profile_name)

    user = Users(auth_type, profile_id, role, username, password, email, identity_provider_id)
    return insert_into_db(user)


def delete_from_db(obj) -> Tuple[bool, Optional[Exception]]:
    if not obj:
        # TODO add logging if obj does not exist
        return True, None
    try:
        db.session.delete(obj)
        db.session.commit()
        return True, None
    except exc.IntegrityError as e:
        db.session().rollback()
        return False, e


def delete_user_username(username: str) -> Tuple[bool, Optional[Exception]]:
    user = Users.query.filter(Users.username == username).first()
    return delete_from_db(user)


def delete_user_email(email: str) -> Tuple[bool, Optional[Exception]]:
    user = Users.query.filter(Users.email == email).first()
    return delete_from_db(user)


def delete_profile(name: str) -> Tuple[bool, Optional[Exception]]:
    profile = Profiles.query.filter(Profiles.name == name).first()
    return delete_from_db(profile)


def delete_identity_provider(id_openeo: str) -> Tuple[bool, Optional[Exception]]:
    identity_provider = IdentityProviders.query.filter(IdentityProviders.id_openeo == id_openeo).first()
    return delete_from_db(identity_provider)


def get_identity_provider_id(identity_provider: str = None) -> Optional[str]:
    if identity_provider:
        return db.session.query(IdentityProviders.id).filter(IdentityProviders.id_openeo == identity_provider).scalar()


def get_profile_id(profile_name: str) -> str:
    return db.session.query(Profiles.id).filter(Profiles.name == profile_name).scalar()
