''' Utils for user service test '''

import datetime
import random
import string
from service import db
from service.model.user import User


def add_user(username, email, password, created_at=datetime.datetime.utcnow(), admin=False):
    ''' Add a user to the database '''

    user = User(username=username,
                email=email,
                password=password,
                created_at=created_at,
                admin=admin)

    db.session.add(user)
    db.session.commit()

    return user

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    ''' Creates a random user name '''

    return ''.join(random.choice(chars) for _ in range(size))

def add_random_user(created_at=datetime.datetime.utcnow(), admin=False):
    ''' Adds a random generated user to the database '''

    name_gen = id_generator()

    user = User(username=name_gen,
                email=name_gen + "@eodc.eu",
                password="test",
                created_at=created_at,
                admin=admin)

    db.session.add(user)
    db.session.commit()

    return user

def get_random_user_dict(username=True, email=True, password=True):
    ''' Returns a dict object of a rondom generated user '''

    name_gen = id_generator()

    user = dict()
    if username:
        user["username"] = name_gen
    if email:
        user["email"] = name_gen + "@eodc.eu"
    if password:
        user["password"] = "test"

    return user
