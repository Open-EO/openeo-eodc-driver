''' API Utilities '''

from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.exc import OperationalError
from flask import jsonify
from functools import wraps
from flask import request, jsonify
from service.model.user import User
from service.api.api_exceptions import AuthenticationError

def parse_response(code, msg=None, data=None):
    ''' Helper for Parsing JSON Response '''

    if msg and data:
        return jsonify({"message": str(msg), "data": data}), code

    if not msg:
        return jsonify(data), code
    
    if not data:
        return str(msg), code


def authenticate(f):
    ''' Create wrapper function for authentication '''
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ''' Decorator function for authentication '''

        try:
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                raise AuthenticationError

            token_split = auth_header.split(" ")
            if len(token_split) != 2:
                raise InvalidTokenError

            auth_token = token_split[1]

            if not auth_token:
                raise AuthenticationError

            user_id = User.decode_auth_token(auth_token)
            user = User.query.filter_by(id=user_id).first()

            if not user or not user.active:
                raise AuthenticationError("User does not exist or is not active.")

        except AuthenticationError as exp:
            return parse_response(exp.code, str(exp))
        except ExpiredSignatureError:
            return parse_response(401, "Signature expired. Please log in again.")
        except InvalidTokenError:
            return parse_response(401, "Invalid token. Please log in again.")
        except OperationalError as exp:
            return parse_response(503, "The service is currently unavailable.")

        return f(user_id, *args, **kwargs)
    return decorated_function


def is_admin(user_id):
    ''' Utility function to check if user is admin '''

    user = User.query.filter_by(id=user_id).first()
    return user.admin
