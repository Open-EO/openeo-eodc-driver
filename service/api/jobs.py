''' EODC Job service '''

from requests.exceptions import RequestException, HTTPError
from flask import Blueprint, request
from service.api.utils import parse_response, authenticate
from service.src.validation import validate_payload, ValidationException
from service.src.process_graph.process_graph import ProcessGraph
from service.src.job import Job

JOBS_BLUEPRINT = Blueprint("jobs", __name__)

@JOBS_BLUEPRINT.route("/jobs", methods=["POST"])
@authenticate
def perform_graph_execution(user):
    ''' Submit a new job to the backend '''

    payload = request.get_json()

    try:
        validate_payload(payload)
    except HTTPError as exp:
        return parse_response(exp.response.status_code, exp.args[0])
    except RequestException as exp:
        return parse_response(503, "Could not connect to API backend. Please contact support.")
    except ValidationException as exp:
        return parse_response(400, "Payload validation failed: " + str(exp))

    process_graph = ProcessGraph(payload)
    job = Job(user.id, process_graph)

    return parse_response(200, "Job {0} sucessfully created".format(job.id))
