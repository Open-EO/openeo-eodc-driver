''' /health route of Process Service '''

from flask import Blueprint
from service.api.api_utils import parse_response

HEALTH_BLUEPRINT = Blueprint("health", __name__)

@HEALTH_BLUEPRINT.route("/health", methods=["GET"])
def health():
    ''' Check health of service '''

    return parse_response(200, "Running!")
