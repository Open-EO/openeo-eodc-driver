''' /data route of Data Service '''

from flask import Blueprint
from .api_utils import parse_response, cors

CAPABILITIES_BLUEPRINT = Blueprint("capabilities", __name__)

@CAPABILITIES_BLUEPRINT.route("/capabilities", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def options_get_capabilities():
    return parse_response(200)

@CAPABILITIES_BLUEPRINT.route("/capabilities", methods=["GET"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def get_capabilities():
    ''' Get data records from PyCSW server '''

    capabilities = [
        "/capabilities",
        "/capabilities/output_formats",
        "/capabilities/services",
        "/data",
        "/data/{product_id}",
        "/processes",
        "/processes/{process_id}",
        "/auth/login",
        "/jobs",
        "/jobs/{job_id}",
        "/jobs/{job_id}/queue",
        "/jobs/{job_id}/download"
    ]

    return parse_response(200, data=capabilities)

@CAPABILITIES_BLUEPRINT.route("/capabilities/output_formats", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def options_output_formats():
    return parse_response(200)

@CAPABILITIES_BLUEPRINT.route("/capabilities/output_formats", methods=["GET"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def get_output_formats():
    ''' Get data records from PyCSW server '''
    
    output_formats = {
        "default": "GTiff",
        "formats": {
            "GTiff": {
            }
        }
    }

    return parse_response(200, data=output_formats)

@CAPABILITIES_BLUEPRINT.route("/capabilities/services", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def options_services():
    return parse_response(200)

@CAPABILITIES_BLUEPRINT.route("/capabilities/services", methods=["GET"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def get_services():
    ''' Get data records from PyCSW server '''
    
    services = []

    return parse_response(200, data=services)