''' Health check for EODC Job Service '''

from flask import Blueprint
from service.api.utils import parse_response

HEALTH_BLUEPRINT = Blueprint("health", __name__)

@HEALTH_BLUEPRINT.route("/health", methods=["GET"])
def ping():
    ''' Check Health '''

    return parse_response(200, "Running!")
