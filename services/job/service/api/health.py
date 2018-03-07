''' /health route of Job Service '''

from flask import Blueprint
from service.api.api_utils import parse_response, cors

HEALTH_BLUEPRINT = Blueprint("health", __name__)

@HEALTH_BLUEPRINT.route("/health", methods=["GET"])
@cors()
def health():
    ''' Check Health of Service '''

    return parse_response(200, "Running!")
