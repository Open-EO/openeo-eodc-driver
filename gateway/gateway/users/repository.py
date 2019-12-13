import os
from typing import List

from sqlalchemy import exc
from gateway.users.models import db, Users, IdentityProviders
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

def verify_auth_token(token):
    # Verify token
    s = Serializer(os.environ.get('SECRET_KEY'))
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None  # valid token, but expired
    except BadSignature:
        return None  # invalid token

    # Verify user exists
    user = db.session.query(Users).filter(Users.id == data['id']).scalar()
    
    return user.id


def insert_identity_provider(issuer_url: str, scopes: List[str], title: str, description: str = None):
    id_provider = IdentityProviders(issuer_url, scopes, title, description)
    try:
        db.session.add(id_provider)
        db.session.commit()
    except exc.IntegrityError as e:
        db.session().rollback()


def insert_users(auth_type: str, username: str = None, password: str = None, email: str = None,
                 identity_provider: str = None):
    identity_provider_id = get_identity_provider_id(identity_provider)
    user = Users(auth_type, username, password, email, identity_provider_id)
    try:
        db.session.add(user)
        db.session.commit()
    except exc.IntegrityError as e:
        db.session().rollback()


def get_identity_provider_id(identity_provider: str = None):
    if identity_provider:
        identity_provider_id = db.session.query(IdentityProviders.id).filter(IdentityProviders.title == identity_provider).scalar()
    
    return identity_provider
