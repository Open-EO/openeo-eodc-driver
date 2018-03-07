''' /users route of User Service '''

import datetime
from flask import Blueprint, jsonify, request, make_response
from sqlalchemy import exc, or_
from sqlalchemy.exc import OperationalError
from service import DB
from service.model.user import User
from service.api.api_utils import parse_response, authenticate, is_admin, cors
from service.api.api_exceptions import InvalidRequest, AuthorizationError, ValidationError
from service.api.api_validation import validate_user

USERS_BLUEPRINT = Blueprint("users", __name__)

@USERS_BLUEPRINT.route("/users", methods=["POST"])
@cors(auth=True, methods=["GET", "POST"])
@authenticate
def add_user(req_uid):
    ''' Add a user to the database. '''

    try:
        if not is_admin(req_uid):
            raise AuthorizationError

        payload = request.get_json()

        if not payload:
            raise InvalidRequest("Invalid payload.")

        validate_user(payload)

        username = payload.get("username")
        email = payload.get("email")
        admin = payload.get("admin")
        password = payload.get("password")

        ex_user = User.query.filter_by(username=username).first()
        ex_email = User.query.filter_by(email=email).first()
        
        if ex_user or ex_email:
            raise InvalidRequest("The username or e-mail already exists.")
        
        new_user = User(
            username=username,
            password=password,
            email=email,
            admin=admin)

        DB.session.add(new_user)
        DB.session.commit()

        return parse_response(201, "{0} successfully created.".format(username))

    except (AuthorizationError, ValidationError, InvalidRequest) as exp:
        return parse_response(exp.code, str(exp))
    except (exc.IntegrityError, ValueError):
        return parse_response(400, "Invalid payload.")
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@USERS_BLUEPRINT.route("/users/<user_id>", methods=["GET"])
@cors(auth=True, methods=["GET", "POST", "DELETE"])
@authenticate
def get_user(req_uid, user_id):
    ''' Get detail of user '''

    try:
        user_id = int(user_id) 
        req_user = User.query.filter_by(id=req_uid).first()

        if req_user.id != user_id and not is_admin(req_uid):
            raise AuthorizationError

        user = User.query.filter_by(id=user_id).first()

        if not user:
            raise ValueError

        return parse_response(200, data=user.get_dict())

    except AuthorizationError as exp:   
        return parse_response(exp.code, str(exp))
    except ValueError:
        return parse_response(404, "The user does not exist.")
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@USERS_BLUEPRINT.route("/users", methods=["GET"])
@cors(auth=True, methods=["GET", "POST"])
@authenticate
def get_all_users(req_uid):
    ''' Get all users '''

    try:
        if not is_admin(req_uid):
            raise AuthorizationError
        
        users = User.query.order_by(User.created_at.desc()).all()

        all_users = []
        for user in users:
            all_users.append(user.get_dict())

        return parse_response(200, data=all_users)

    except AuthorizationError as exp:
        return parse_response(exp.code, str(exp))
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@USERS_BLUEPRINT.route("/users/<user_id>", methods=["DELETE"])
@cors(auth=True, methods=["GET", "POST", "DELETE"])
@authenticate
def delete_user(req_uid, user_id):
    ''' Delete an user '''

    try:
        user_id = int(user_id)
        req_user = User.query.filter_by(id=req_uid).first()

        if req_user.id != user_id and not is_admin(req_uid):
            raise AuthorizationError

        user = User.query.filter_by(id=user_id).first()

        if not user:
            raise ValueError

        DB.session.delete(user)
        DB.session.commit()

        return parse_response(200, "{0} successfully deleted.".format(user.username))

    except AuthorizationError as exp:
        return parse_response(exp.code, str(exp))
    except ValueError:
         return parse_response(404, "User does not exist.")
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@USERS_BLUEPRINT.route("/users/<user_id>", methods=["POST"])
@cors(auth=True, methods=["GET", "POST", "DELETE"])
@authenticate
def change_user(req_uid):
    ''' Change users details '''

    try:
        if not is_admin(req_uid):
            raise AuthorizationError

        payload = request.get_json()

        if not payload:
            raise InvalidRequest("Invalid payload.")

        validate_user(payload)

        username = payload.get("username")
        email = payload.get("email")
        admin = payload.get("admin")
        password = payload.get("password")

        ex_user = User.query.filter_by(username=username).first()

        ex_user.username = username
        ex_user.email = email
        ex_user.password = User.generate_hash(password)
        ex_user.admin = admin

        DB.session.commit()

        return parse_response(201, "{0} successfully created.".format(username))

    except (AuthorizationError, ValidationError, InvalidRequest) as exp:
        return parse_response(exp.code, str(exp))
    except (exc.IntegrityError, ValueError):
        return parse_response(400, "Invalid payload.")
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")