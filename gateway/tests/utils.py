""" Utils for user service test """

from datetime import datetime
import random
import string
from typing import Dict
from uuid import uuid4

from passlib.apps import custom_app_context as pwd_context

from gateway.users.models import AuthType, db, Profiles, Users


def id_generator(size: int = 6, chars=string.ascii_uppercase + string.digits):
    """ Creates a random user name """

    return ''.join(random.choice(chars) for _ in range(size))


def add_profile(name: str, data_access: str) -> Profiles:
    """ Add a profile to the database """
    profile = Profiles(
        id=id_generator(10),
        name=name,
        data_access=data_access,
    )

    db.session.add(profile)
    db.session.commit()

    return profile


def get_password_hash(password: str) -> str:
    return pwd_context.encrypt(password)


def add_basic_user(username, password, profile_id: str, role: str = 'user', created_at: datetime = datetime.utcnow()) \
        -> Users:
    """ Add a user to the database """

    user = Users(
        id=f"us-{uuid4()}",
        username=username,
        password_hash=get_password_hash(password),
        auth_type=AuthType.basic,
        role=role,
        profile_id=profile_id,
        created_at=created_at,
    )

    db.session.add(user)
    db.session.commit()
    return user


def add_random_profile(name: str = "public", data_access: str = "public") -> Profiles:
    profile_name_gen = name if name else id_generator()
    return add_profile(name=profile_name_gen, data_access=data_access)


def add_random_basic_user(profile_id: str, created_at: datetime = datetime.utcnow(), role: str = "user") -> Users:
    """ Adds a random generated user to the database """

    user_name_gen = id_generator()
    user = add_basic_user(username=user_name_gen, password="test", role=role, profile_id=profile_id,
                          created_at=created_at)
    return user


def get_random_user_dict(username: bool = True, password: bool = True, profile: bool = True) -> Dict[str, str]:
    """ Returns a dict object of a random generated user """

    name_gen = id_generator()

    user = {}
    if username:
        user["username"] = name_gen
    if password:
        user["password"] = "test"
    if profile:
        user["profile"] = "public"

    return user
