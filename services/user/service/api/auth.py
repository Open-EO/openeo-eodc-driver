''' /auth route of User Service '''

from flask import Blueprint, request, current_app
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import OperationalError
from base64 import b64decode
from service import BCRYPT
from service.model.user import User
from service.api.api_utils import parse_response, authenticate, cors
from service.api.api_exceptions import InvalidRequest, AuthenticationError

AUTH_BLUEPRINT = Blueprint("auth", __name__)

@AUTH_BLUEPRINT.route("/auth/login", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def options_auth_login():
    return parse_response(200)

@AUTH_BLUEPRINT.route("/auth/login", methods=["GET"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def login_user():
    ''' Check credentials and send auth token '''

    try:
        username = request.authorization["username"]
        password = request.authorization["password"]

        if not username or not password:
            raise InvalidRequest("Missing username or password.")
        
        user = User.query.filter_by(username=username).first()

        if not user:
            raise AuthenticationError("User does not exist.")

        if not BCRYPT.check_password_hash(user.password, password):
            raise AuthenticationError("Username or Password wrong.")

        auth_token = user.encode_auth_token(user.id)

        return parse_response(200, data={"token": auth_token.decode(), "user_id":user.id})

    except (InvalidRequest, AuthenticationError) as exp:
        return parse_response(exp.code, str(exp))
    except BadRequest as exp:
        return parse_response(400, "Could not parse payload.")
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")


@AUTH_BLUEPRINT.route("/auth/logout", methods=["GET"])
@cors(auth=True, methods=["GET"])
@authenticate
def logout_user(req_uid):
    ''' Get auth token and log out '''
    return parse_response(200, "Successfully logged out.")

@AUTH_BLUEPRINT.route("/auth/verify", methods=["GET"])
@cors(auth=True, methods=["GET"])
@authenticate
def verify_user(req_uid):
    ''' Verify auth token and return users id '''
    return parse_response(200, req_uid)

@AUTH_BLUEPRINT.route("/auth/identify", methods=["GET"])
@cors(auth=True, methods=["GET"])
@authenticate
def identify_user(req_uid):
    '''Return users identity '''
    try:
        user = User.query.filter_by(id=req_uid).first()

        if not user:
            raise AuthenticationError("User does not exist.")

        return parse_response(200, data=user.get_dict())

    except AuthenticationError as exp:
        return parse_response(exp.code, str(exp))
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")
