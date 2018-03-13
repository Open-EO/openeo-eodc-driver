''' /jobs route of Job Service '''

from os import listdir, path
from requests.exceptions import RequestException, HTTPError
from sqlalchemy.exc import OperationalError
from flask import Blueprint, request, send_from_directory, current_app
from service import DB
from .api_utils import parse_response, authenticate, cors
from .api_exceptions import InvalidRequest, AuthorizationError
from service.model.job import Job
from worker.tasks import start_job_processing
from worker.src.validation import validate_job, ValidationError

JOBS_BLUEPRINT = Blueprint("jobs", __name__)

@JOBS_BLUEPRINT.route("/jobs", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "POST"])
def options_jobs():
    return parse_response(200)

@JOBS_BLUEPRINT.route("/jobs", methods=["POST"])
@cors(auth=True, methods=["OPTIONS", "POST"])
@authenticate
def create_job(req_user, auth):
    ''' Submits a new job to the back-end '''
    try:
        payload = request.get_json()

        if not payload:
            raise InvalidRequest("Invalid payload.")

        validate_job(payload)

        job = Job(user_id=req_user["id"], task=payload)

        DB.session.add(job)
        DB.session.commit()

        # TODO Message Broker
        # TODO Logging

        return parse_response(200, data=job.get_small_dict())

    except ValidationError as exp:
        return parse_response(exp.code, str(exp))
    except InvalidRequest as exp:
        return parse_response(exp.code, str(exp))
    except HTTPError as exp:
        return parse_response(exp.response.status_code, exp.args[0])
    except RequestException as exp:
        return parse_response(503, "Could not connect to API backend. Please contact support.")
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@JOBS_BLUEPRINT.route("/jobs/<job_id>", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "GET", "DELETE"])
def options_jobs_id(job_id):
    return parse_response(200)

@JOBS_BLUEPRINT.route("/jobs/<job_id>", methods=["GET"])
@cors(auth=True, methods=["OPTIONS", "GET", "DELETE"])
@authenticate
def get_job(req_user, auth, job_id):
    ''' Returns detailed information about a submitted job including its current status and the underlying task '''

    try:
        job = Job.query.filter_by(id=job_id).first()

        if not job:
            raise InvalidRequest("Job with specified identifier is not available.")

        if req_user["id"] != job.user_id and not req_user["admin"]:
            raise AuthorizationError
        
        return parse_response(200, data=job.get_dict())

    except (InvalidRequest, AuthorizationError) as exp:
        return parse_response(exp.code, str(exp))
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@JOBS_BLUEPRINT.route("/jobs/<job_id>/queue", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "PATCH"])
def options_jobs_queue(job_id):
    return parse_response(200)

@JOBS_BLUEPRINT.route("/jobs/<job_id>/queue", methods=["PATCH"])
@cors(auth=True, methods=["OPTIONS", "PATCH"])
@authenticate
def queue_job(req_user, auth, job_id):
    ''' Returns detailed information about a submitted job including its current status and the underlying task '''

    try:
        job = Job.query.filter_by(id=job_id).first()

        if not job:
            raise InvalidRequest("Job with specified identifier is not available.")

        if req_user["id"] != job.user_id and not req_user["admin"]:
            raise AuthorizationError
        
        start_job_processing.delay(job.get_dict())
        # start_job_processing(job.get_dict())

        return parse_response(200, msg="The job has been successfully queued.")

    except (InvalidRequest, AuthorizationError) as exp:
        return parse_response(exp.code, str(exp))
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")


@JOBS_BLUEPRINT.route("/jobs/<job_id>/execute", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def options_jobs_execute(job_id):
    return parse_response(200)

@JOBS_BLUEPRINT.route("/jobs/<job_id>/execute", methods=["GET"])
@cors(auth=True, methods=["OPTIONS", "GET"])
@authenticate
def execute_job(req_user, auth, job_id):
    ''' Executes a job '''

    try:
        job = Job.query.filter_by(id=job_id).first()

        if not job:
            raise InvalidRequest("Job with specified identifier is not available.")

        if req_user["id"] != job.user_id and not req_user["admin"]:
            raise AuthorizationError
        
        # TODO: Job Runtime handling
        # TODO: Download Link return
        start_job_processing(job.get_dict())

        return parse_response(200, data={"job_id": job.id})

    except (InvalidRequest, AuthorizationError) as exp:
        return parse_response(exp.code, str(exp))
    except RequestException as exp:
        return parse_response(503, "Could not connect to API backend. Please contact support.")
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@JOBS_BLUEPRINT.route("/jobs/<job_id>/status", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "POST"])
def options_jobs_status(job_id):
    return parse_response(200)

@JOBS_BLUEPRINT.route("/jobs/<job_id>/status", methods=["POST"])
@cors(auth=True, methods=["OPTIONS", "POST"])
# @authenticate
# TODO: Message Broker
def update_status(job_id):
    ''' Updates the status of the job '''

    try:
        payload = request.get_json()

        if not payload:
            raise InvalidRequest("Invalid payload.")

        job = Job.query.filter_by(id=job_id).first()

        if not job:
            raise InvalidRequest("Job with specified identifier is not available.")

        job.status = payload["status"]
        DB.session.commit()

        return parse_response(200, data={"job_id": job.id})
    except InvalidRequest as exp:
        return parse_response(exp.code, str(exp))
    except HTTPError as exp:
        return parse_response(exp.response.status_code, exp.args[0])
    except RequestException as exp:
        return parse_response(503, "Could not connect to API backend. Please contact support.")
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@JOBS_BLUEPRINT.route("/jobs/<job_id>", methods=["DELETE"])
@cors(auth=True, methods=["OPTIONS", "GET", "DELETE"])
@authenticate
def delete_job(req_user, auth, job_id):
    ''' Deleting a job will cancel execution at the back-end regardless of its status. For finished jobs, this will also delete resulting data. '''

    try:
        job = Job.query.filter_by(id=job_id).first()

        if not job:
            raise InvalidRequest("Job with specified identifier is not available.")

        if req_user["id"] != job.user_id and not req_user["admin"]:
            raise AuthorizationError

        DB.session.delete(job)
        DB.session.commit()

        return parse_response(200, data=job.get_dict())

    except (InvalidRequest, AuthorizationError) as exp:
        return parse_response(exp.code, str(exp))
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@JOBS_BLUEPRINT.route("/jobs/<job_id>/download", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def options_jobs_download(job_id):
    return parse_response(200)

@JOBS_BLUEPRINT.route("/jobs/<job_id>/download", methods=["GET"])
@cors(auth=True, methods=["OPTIONS", "GET"])
@authenticate
def download_result(req_user, auth, job_id):
    ''' Downloading job results '''

    try:
        job = Job.query.filter_by(id=job_id).first()

        if not job:
            raise InvalidRequest("Job with specified identifier is not available.")

        if req_user["id"] != job.user_id and not req_user["admin"]:
            raise AuthorizationError

        job_directory = "/job_results/{0}".format(job_id)

        if not path.isdir(job_directory):
            raise InvalidRequest("Files are not (yet) available for job with id {0}.".format(job_id)) 

        file_links = []
        for file_name in listdir(job_directory):
            file_links.append("{0}/download/{1}/{2}".format(current_app.config["OPENEO_API"], job_id, file_name))

        return parse_response(200, data=file_links)

    except (InvalidRequest, AuthorizationError) as exp:
        return parse_response(exp.code, str(exp))
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")