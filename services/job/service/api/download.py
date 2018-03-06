''' /jobs route of Job Service '''

from os import listdir
from requests.exceptions import RequestException, HTTPError
from sqlalchemy.exc import OperationalError
from flask import Blueprint, request, send_from_directory, current_app
from flask_cors import cross_origin
from service import DB
from service.api.api_utils import parse_response, authenticate
from service.api.api_exceptions import InvalidRequest, AuthorizationError
from service.model.job import Job

DOWNLOAD_BLUEPRINT = Blueprint("downloads", __name__)

@DOWNLOAD_BLUEPRINT.route("/download/<job_id>/<file_name>", methods=["GET"])
@cross_origin(origins="*", supports_credentials=True)
@authenticate
def get_results(req_user, auth, job_id, file_name):
    ''' Returns the processed files '''

    try:
        job = Job.query.filter_by(id=job_id).first()

        if not job:
            raise InvalidRequest("Job with specified identifier is not available.")

        if req_user["id"] != job.user_id and not req_user["admin"]:
            raise AuthorizationError

        job_directory = "/job_results/{0}".format(job_id)

        files_in_dir = listdir(job_directory)

        if not file_name in files_in_dir:
            raise InvalidRequest("File is not available for job with id {0}.".format(job_id)) 

        return send_from_directory(directory=job_directory, filename=file_name)

    except (InvalidRequest, AuthorizationError) as exp:
        return parse_response(exp.code, str(exp))
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")
