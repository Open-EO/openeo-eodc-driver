''' /health route of Data Service '''

from flask import Blueprint
from .api_utils import parse_response, cors

HEALTH_BLUEPRINT = Blueprint("health", __name__)

@HEALTH_BLUEPRINT.route("/health", methods=["GET"])
@cors()
def health():
    ''' Check health of service '''
    return parse_response(200, "Running!")
