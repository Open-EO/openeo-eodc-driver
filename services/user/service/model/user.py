''' Model of User '''

import jwt
import datetime
from flask import current_app
from service import DB, BCRYPT

class User(DB.Model):
    __tablename__ = "users"

    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True) # Umbennen in uid
    username = DB.Column(DB.String(128), unique=True, nullable=False)
    email = DB.Column(DB.String(128), unique=True, nullable=False)
    password = DB.Column(DB.String(255), nullable=False)
    admin = DB.Column(DB.Boolean, default=False, nullable=False)
    active = DB.Column(DB.Boolean, default=True, nullable=False)
    created_at = DB.Column(DB.DateTime, nullable=False)

    def __init__(self, username, email, password, created_at=datetime.datetime.utcnow(), admin=False):
        self.username = username
        self.email = email
        self.password = self.generate_hash(password)
        self.admin = admin
        self.created_at = created_at
    
    def get_dict(self):
        ''' Returns the users data '''
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "admin": self.admin,
            "created_at": self.created_at
        }

    @staticmethod
    def generate_hash(password):
        ''' Generates the password hash '''
        return BCRYPT.generate_password_hash(password, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()

    @staticmethod
    def encode_auth_token(user_id):
        ''' Generates the auth token '''

        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(
                days=current_app.config.get('TOKEN_EXPIRATION_DAYS'),
                seconds=current_app.config.get('TOKEN_EXPIRATION_SECONDS')
            ),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }

        return jwt.encode(payload, current_app.config.get('SECRET_BCRYPT'), algorithm='HS256')

    @staticmethod
    def decode_auth_token(auth_token):
        ''' Decodes the auth token '''

        payload = jwt.decode(auth_token, current_app.config.get('SECRET_BCRYPT'))

        return payload['sub']
