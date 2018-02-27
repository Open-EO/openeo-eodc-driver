''' /auth route of User Service '''

from flask import Blueprint, request, current_app
from flask_cors import cross_origin
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import OperationalError
from service import BCRYPT
from service.model.user import User
from service.api.api_utils import parse_response, authenticate
from service.api.api_exceptions import InvalidRequest, AuthenticationError

AUTH_BLUEPRINT = Blueprint("auth", __name__)

@AUTH_BLUEPRINT.route("/auth/login", methods=["POST"])
def login_user():
    ''' Check credentials and send auth token '''

    try:
        if not request.is_json: 
            raise InvalidRequest("Request needs to be JSON.")

        payload = request.get_json()
        
        if not "username" in payload or not "password" in payload:
            raise InvalidRequest("Missing username or password.")

        username = payload.get("username")
        password = payload.get("password")

        if not username or not password:
            raise InvalidRequest("Missing username or password.")
        
        user = User.query.filter_by(username=username).first()

        if not user:
            raise AuthenticationError("User does not exist.")

        if not BCRYPT.check_password_hash(user.password, password):
            raise AuthenticationError("Username or Password wrong.")

        auth_token = user.encode_auth_token(user.id)

        return parse_response(200, "Successfully logged in.", 
                                    data={"auth_token": auth_token.decode(), 
                                    "admin":user.admin})

    except (InvalidRequest, AuthenticationError) as exp:
        return parse_response(exp.code, str(exp))
    except BadRequest as exp:
        return parse_response(400, "Could not parse payload.")
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")


@AUTH_BLUEPRINT.route("/auth/logout", methods=["GET"])
@cross_origin(supports_credentials=True)
@authenticate
def logout_user(req_uid):
    ''' Get auth token and log out '''
    return parse_response(200, "Successfully logged out.")

@AUTH_BLUEPRINT.route("/auth/verify", methods=["GET"])
@cross_origin(origins="*", supports_credentials=True)
@authenticate
def verify_user(req_uid):
    ''' Verify auth token and return users id '''
    return parse_response(200, req_uid)

@AUTH_BLUEPRINT.route("/auth/identify", methods=["GET"])
@cross_origin(origins="*", supports_credentials=True)
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
