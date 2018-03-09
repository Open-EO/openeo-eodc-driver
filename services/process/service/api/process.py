''' /processes route of Process Service '''

from flask import Blueprint, request, current_app
from sqlalchemy.exc import OperationalError
from service import DB
from service.model.process import Process
from service.api.api_utils import parse_response, authenticate, cors
from service.api.api_exceptions import ValidationError, InvalidRequest, AuthorizationError
from service.api.api_validation import validate_process

PROCESS_BLUEPRINT = Blueprint("process", __name__)

@PROCESS_BLUEPRINT.route("/processes", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "GET", "POST"])
def options_process():
    return parse_response(200)

@PROCESS_BLUEPRINT.route("/processes", methods=["POST"])
@cors(auth=True, methods=["OPTIONS", "GET", "POST"])
@authenticate
def add_process(req_user):
    ''' Add a process to the registry'''

    try:
        if not req_user["admin"]:
            raise AuthorizationError

        payload = request.get_json()

        if not payload:
            raise InvalidRequest("Invalid payload.")

        validate_process(payload)

        process_id = payload["process_id"]
        description = payload["description"]
        process_type = payload["type"]
        args = payload["args"]

        if process_type == "operation":
            git_uri = payload["git_uri"]
            git_ref = payload["git_ref"]
            git_dir = payload["git_dir"]
        else:
            git_uri = None
            git_ref = None
            git_dir = None

        does_exist = Process.query.filter_by(process_id=process_id).first()

        if does_exist:
            raise InvalidRequest("The process already exists.")

        process = Process(
            user_id = req_user["id"],
            process_id=process_id,
            description=description,
            git_uri=git_uri,
            git_ref=git_ref,
            git_dir=git_dir,
            process_type=process_type,
            args=args)

        DB.session.add(process)
        DB.session.commit()

        return parse_response(200, data={"process_id": process.id})

    except (AuthorizationError, ValidationError, InvalidRequest) as exp:
        return parse_response(exp.code, str(exp))
    except ValueError as exp:
        return parse_response(400, "Invalid payload.")
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@PROCESS_BLUEPRINT.route("/processes", methods=["GET"])
@cors(auth=True, methods=["GET", "POST"])
# @authenticate
def get_all_processes():
    ''' Information about all processes that are available '''
    # TODO: Authentification / service message broker
    
    try:
        processes = Process.query.order_by(Process.process_id).all()

        all_processes = []
        for process in processes:
            desc = process.get_description()
            desc["process_id"] = desc["process_id"].lower()

            if desc["process_id"] == "min-time":
                desc["process_id"] = "min_time"
            
            if desc["process_id"] == "ndvi":
                desc["process_id"] = "NDVI"

            all_processes.append(desc)

        return parse_response(200, data=all_processes)

    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@PROCESS_BLUEPRINT.route("/processes/<process_id>", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "GET", "DELETE", "PUT"])
def options_process_id(process_id):
    return parse_response(200)

@PROCESS_BLUEPRINT.route("/processes/<process_id>", methods=["GET"])
@cors(auth=True, methods=["OPTIONS", "GET", "DELETE", "PUT"])
# @authenticate
def get_process(process_id):
    ''' Information about specific process '''
    # TODO: Authentification / service message broker
    
    try:
        process_id = process_id.lower()

        if process_id == "min_time":
            process_id = "min-time"
        
        process = Process.query.filter_by(process_id=process_id).first()

        if not process:
            raise InvalidRequest("Process does not exist.")

        return parse_response(200, data=process.get_small_dict())

    except InvalidRequest as exp:
        return parse_response(exp.code, str(exp))
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@PROCESS_BLUEPRINT.route("/processes/<process_id>/details", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def options_process_id_details(process_id):
    return parse_response(200)

@PROCESS_BLUEPRINT.route("/processes/<process_id>/details", methods=["GET"])
@cors(auth=True, methods=["OPTIONS", "GET"])
# @authenticate
def get_process_details(process_id):
    ''' Detailed information about specific process that includes sensitive information '''
    # TODO: Authentification / service message broker
    
    try:
        process_id = process_id.lower()

        if process_id == "min_time":
            process_id = "min-time"
            
        process = Process.query.filter_by(process_id=process_id).first()

        if not process:
            raise InvalidRequest("Process does not exist.")

        return parse_response(200, data=process.get_dict())

    except InvalidRequest as exp:
        return parse_response(exp.code, str(exp))
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@PROCESS_BLUEPRINT.route("/processes/<process_id>", methods=["DELETE"])
@cors(auth=True, methods=["OPTIONS", "GET", "DELETE", "PUT"])
@authenticate
def delete_process(req_user, process_id):
    ''' Delete process '''

    try:
        if not req_user["admin"]:
            raise AuthorizationError

        process = Process.query.filter_by(process_id=process_id).first()

        if not process:
            raise InvalidRequest("Process does not exist.")

        DB.session.delete(process)
        DB.session.commit()

        return parse_response(200, "Process {0} sucesssfully deleted.".format(process_id))

    except (InvalidRequest, AuthorizationError) as exp:
        return parse_response(exp.code, str(exp))
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")


@PROCESS_BLUEPRINT.route("/processes/<process_id>", methods=["PUT"])
@cors(auth=True, methods=["OPTIONS", "GET", "DELETE", "PUT"])
@authenticate
def alter_process(req_user, process_id):
    ''' Alter values of process in namespace'''

    try:
        if not req_user["admin"]:
            raise AuthorizationError

        payload = request.get_json()

        if not payload:
            raise InvalidRequest("Invalid payload.")

        validate_process(payload)

        process = Process.query.filter_by(process_id=process_id).first()

        if not process:
            raise InvalidRequest("Process does not exist.")

        process.process_id = payload["process_id"]
        process.description = payload["description"]
        process.process_type = payload["type"]
        process.args = payload["args"]

        if payload["type"] == "operation":
            process.git_uri = payload["git_uri"]
            process.git_ref = payload["git_ref"]
            process.git_dir = payload["git_dir"]

        DB.session.commit()

        return parse_response(200, "Process {0} sucesssfully altered.".format(process_id))

    except (InvalidRequest, AuthorizationError) as exp:
        return parse_response(exp.code, str(exp))
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@PROCESS_BLUEPRINT.route("/processes/opensearch", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS, GET"])
def options_process_id_opensearch():
    return parse_response(200)

@PROCESS_BLUEPRINT.route("/processes/opensearch", methods=["GET"])
@cors(auth=True, methods=["OPTIONS, GET"])
# @authenticate
def get_process_opensearch(req_user, process_id):
    ''' Get process using opensearch'''

    # TODO: Implement!
    return parse_response(501, "This API feature is not supported by the back-end.")