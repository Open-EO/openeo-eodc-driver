''' EODC Job service '''

from flask import Blueprint, request
from service.api.utils import parse_response
from service.src.validation import validate_payload, ValidationException
from service.src.node import parse_process_graph, ParsingException

JOBS_BLUEPRINT = Blueprint("jobs", __name__)

@ JOBS_BLUEPRINT.route("/jobs", methods=["POST"])
def perform_graph_execution():
    ''' Perform and monitor the execution of a process graph '''

    payload = request.get_json()

    # process_graph = ProcessGraph(payload)

    try:
        process_graph = validate_payload(payload)
        parsed_graph = parse_process_graph(process_graph)

        # parsed_graph.build()
        parsed_graph.deploy()

    except ValidationException as exp:
        return parse_response(400, str(exp))
    except ParsingException as exp:
        return parse_response(400, str(exp))

    return parse_response(200, "Job gnj79kl976ghlk sucessfully created")
