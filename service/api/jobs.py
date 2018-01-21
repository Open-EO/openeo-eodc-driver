''' EODC Job service '''

from flask import Blueprint, request
from service.api.utils import parse_response
from service.src.validation import validate_payload, ValidationException
from service.src.parse import parse_process_graph, ParsingException
JOBS_BLUEPRINT = Blueprint("jobs", __name__)

@ JOBS_BLUEPRINT.route("/jobs", methods=["POST"])
def perform_graph_execution():
    ''' Perform and monitor the execution of a process graph '''

    payload = request.get_json()

    try:
        process_graph = validate_payload(payload)
        start_node = parse_process_graph(process_graph)
    except ValidationException as exp:
        # TODO: Exception Logging
        return parse_response(400, str(exp))
    except ParsingException as exp:
        # TODO: Exception Logging
        return parse_response(400, str(exp))

    return parse_response(200, "Not yet implemented.")
