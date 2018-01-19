''' Health check for benchmarking service '''

from flask import Blueprint
from service.api.utils import parse_response

HEALTH_BLUEPRINT = Blueprint("health", __name__)

@HEALTH_BLUEPRINT.route("/ping", methods=["GET"])
def ping():
    ''' Check service health'''

    return parse_response(200, "pong!")
