''' /jobs route of Job Service '''

from requests.exceptions import RequestException, HTTPError
from sqlalchemy.exc import OperationalError
from flask import Blueprint, request, send_from_directory
from flask_cors import cross_origin
from service import DB
from service.api.api_utils import parse_response, authenticate
from service.api.api_validation import validate_job
from service.api.api_exceptions import ValidationError, InvalidRequest, AuthorizationError, TemplateError
from service.model.job import Job
from worker.tasks import start_job_processing
import timeit

JOBS_BLUEPRINT = Blueprint("jobs", __name__)

@JOBS_BLUEPRINT.route("/jobs", methods=["POST"])
@cross_origin(origins="*", supports_credentials=True)
@authenticate
def create_job(req_user, auth):
    ''' Submits a new job to the back-end '''

    try:
        start = timeit.timeit()


        payload = request.get_json()

        if not payload:
            raise InvalidRequest("Invalid payload.")


        validate_job(payload, auth)

        job = Job(user_id=req_user["id"], task=payload)

        DB.session.add(job)
        DB.session.commit()

        # TODO Make it async (Worker)
        # TODO Message Broker
        # TODO Logging

        start_job_processing(job.get_dict())

        end = timeit.timeit()
        print(end - start)

        return parse_response(200, data={"job_id": job.get_small_dict()})
    except (ValidationError, InvalidRequest) as exp:
        return parse_response(exp.code, str(exp))
    except HTTPError as exp:
        return parse_response(exp.response.status_code, exp.args[0])
    except RequestException as exp:
        return parse_response(503, "Could not connect to API backend. Please contact support.")
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@JOBS_BLUEPRINT.route("/jobs/<job_id>", methods=["GET"])
@cross_origin(origins="*", supports_credentials=True)
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

@JOBS_BLUEPRINT.route("/jobs/<job_id>/execute", methods=["GET"])
@cross_origin(origins="*", supports_credentials=True)
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

    except (InvalidRequest, AuthorizationError, TemplateError) as exp:
        return parse_response(exp.code, str(exp))
    except RequestException as exp:
        return parse_response(503, "Could not connect to API backend. Please contact support.")
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@JOBS_BLUEPRINT.route("/jobs/<job_id>/status", methods=["POST"])
@cross_origin(origins="*")
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
    except (ValidationError, InvalidRequest) as exp:
        return parse_response(exp.code, str(exp))
    except HTTPError as exp:
        return parse_response(exp.response.status_code, exp.args[0])
    except RequestException as exp:
        return parse_response(503, "Could not connect to API backend. Please contact support.")
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")

@JOBS_BLUEPRINT.route("/jobs/<job_id>", methods=["DELETE"])
@cross_origin(origins="*", supports_credentials=True)
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

@JOBS_BLUEPRINT.route("/jobs/<job_id>/download", methods=["DELETE"])
@cross_origin(origins="*", supports_credentials=True)
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

        return send_from_directory(directory=job_directory, filename="results.gpkg")

    except (InvalidRequest, AuthorizationError) as exp:
        return parse_response(exp.code, str(exp))
    except OperationalError as exp:
        return parse_response(503, "The service is currently unavailable.")