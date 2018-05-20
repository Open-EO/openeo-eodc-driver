import datetime as dt
from os import environ
from nameko.extensions import DependencyProvider
from bcrypt import gensalt, hashpw
from jwt import encode, decode
from random import choice
from string import ascii_lowercase, digits


class CryptWrapper:
    def __init__(self, secret, log_rounds, token_expiration_days, token_expiration_seconds):
        self.secret = secret
        self.log_rounds = log_rounds
        self.token_expiration_days = token_expiration_days
        self.token_expiration_seconds = token_expiration_seconds

    def generate_random_string(self, size):
        return "".join(choice(ascii_lowercase + digits) for _ in range(size))

    def generate_hash(self, password, salt=None):
        ''' Generates the password hash '''
        return hashpw(
            password.encode('utf8'),
            gensalt(self.log_rounds) if not salt else salt.encode()
        ).decode()

    def encode_auth_token(self, user_id):
        ''' Generates the auth token '''

        payload = {
            'exp': dt.datetime.utcnow() + dt.timedelta(
                days=self.token_expiration_days,
                seconds=self.token_expiration_seconds
            ),
            'iat': dt.datetime.utcnow(),
            'sub': user_id
        }

        return encode(payload, self.secret, algorithm='HS256').decode()

    def decode_auth_token(self, token):
        ''' Decodes the auth token '''
        return decode(token, self.secret)['sub']


class CryptHandler(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return CryptWrapper(
            environ.get("SECRET"),
            int(environ.get("BCRYPT_LOG_ROUNDS")),
            int(environ.get("TOKEN_EXPIRATION_DAYS")),
            int(environ.get("TOKEN_EXPIRATION_SECONDS")))
