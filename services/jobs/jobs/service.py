""" Job Management """

import logging
import os
from datetime import datetime
from time import sleep
from typing import Tuple, Optional
from uuid import uuid4

from eodc_openeo_bindings.job_writer.dag_writer import AirflowDagWriter
from nameko.rpc import rpc, RpcProxy
from nameko_sqlalchemy import DatabaseSession

from .dependencies.airflow_conn import Airflow
from .models import Base, Job, JobStatus
from .schema import JobShortSchema, JobFullSchema, JobResultsSchema, JobCreateSchema

service_name = "jobs"
LOGGER = logging.getLogger('standardlog')


class ServiceException(Exception):
    """ServiceException raises if an exception occured while processing the
    request. The ServiceException is mapping any exception to a serializable
    format for the API gateway.
    """

    def __init__(self, code: int, user_id: str, msg: str, internal: bool = True, links: list = None):
        if not links:
            links = []

        self._service = service_name
        self._code = code
        self._user_id = user_id
        self._msg = msg
        self._internal = internal
        self._links = links
        LOGGER.exception(msg, exc_info=True)

    def to_dict(self) -> dict:
        """Serializes the object to a dict.

        Returns:
            dict -- The serialized exception
        """

        return {
            "status": "error",
            "service": self._service,
            "code": self._code,
            "user_id": self._user_id,
            "msg": self._msg,
            "internal": self._internal,
            "links": self._links
        }


class JobLocked(ServiceException):
    """ JobLocked raised if job is queued / running when trying to modify it. """
    def __init__(self, code: int, user_id: str, msg: str, internal: bool = True, links: list = None):
        super(JobLocked, self).__init__(code, user_id, msg, internal, links)


class JobNotFinished(ServiceException):
    """ JobNotFinished raised if job is not finished but results are requested . """
    def __init__(self, code: int, user_id: str, job_id: str, msg: str = None, internal: bool = True, links: list = None):
        if not msg:
            msg = f"Job {job_id} is not yet finished. Results cannot be accessed."
        super().__init__(code, user_id, msg, internal, links)


class JobService:
    """Management of batch processing tasks (jobs) and their results.
    """

    name = service_name
    db = DatabaseSession(Base)
    processes_service = RpcProxy("processes")
    files_service = RpcProxy("files")
    airflow = Airflow()
    dag_writer = AirflowDagWriter()
    check_stop_interval = 5  # should be similar or smaller than Airflow sensor's poke interval

    @rpc
    def get(self, user_id: str, job_id: str) -> dict:
        """The request will ask the back-end to get the job using the job_id.

        Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the job
        """
        try:
            job = self.db.query(Job).filter_by(id=job_id).first()
            valid, response = self.authorize(user_id, job_id, job)
            if not valid:
                return response

            self._update_job_status(job_id=job_id)
            response = self.processes_service.get_user_defined(user_id, job.process_graph_id)
            if response["status"] == "error":
                return response
            job.process = response["data"]["process_graph"]

            return {
                "status": "success",
                "code": 200,
                "data": JobFullSchema().dump(job)
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp), links=[]).to_dict()

    @rpc
    def modify(self, user_id: str, job_id: str, **job_args) -> dict:
        """The request will ask the back-end to modify the job with the given job_id.

        Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the job
        """
        try:
            job = self.db.query(Job).filter_by(id=job_id).first()
            valid, response = self.authorize(user_id, job_id, job)
            if not valid:
                return response

            self._update_job_status(job_id=job_id)
            if job.status in [JobStatus.queued, JobStatus.running]:
                return JobLocked(400, user_id, f"Job {job_id} is currently {job.status} and cannot be modified",
                                 links=[]).to_dict()

            if job_args.get("process", None):

                # handle processes db
                process_graph_args = job_args.pop('process')
                process_graph_id = process_graph_args["id"] if "id" in process_graph_args else str(uuid4())
                process_response = self.processes_service.put_user_defined(
                    user_id=user_id, process_graph_id=process_graph_id, **process_graph_args)
                if process_response["status"] == "error":
                    return process_response
                job.process_graph_id = process_graph_id

                # handle dag file (remove and recreate it) - only needs to be updated if process graph changes
                os.remove(self.get_dag_path(job.dag_filename))
                self.dag_writer.write_and_move_job(job_id=job_id, user_name=user_id,
                                                   process_graph_json=process_graph_args['process_graph'],
                                                   job_data=self.get_job_folder(user_id, job_id),
                                                   vrt_only=True, add_delete_sensor=True)

            # Maybe there is a better option to do this update? e.g. using marshmallow schemas?
            job.title = job_args.get("title", job.title)
            job.description = job_args.get("description", job.description)
            job.plan = job_args.get("plan", job.plan)
            if job_args.get("budget", None):
                job.budget = int(job_args["budget"] * 100)
            self.db.commit()

            return {
                "status": "success",
                "code": 204
            }

        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                                    links=[]).to_dict()

    @rpc
    def delete(self, user_id: str, job_id: str) -> dict:
        """The request will ask the back-end to completely delete the job with the given job_id.
        This will stop the job if it is currently queued or running, remove the job itself and all results.

        Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the process graph
        """
        # TODO handle costs (stop it)
        try:
            LOGGER.debug(f"Start deleting job {job_id}")
            job = self.db.query(Job).filter_by(id=job_id).first()
            valid, response = self.authorize(user_id, job_id, job)
            if not valid:
                return response

            self._update_job_status(job_id=job_id)
            if job.status in [JobStatus.running, JobStatus.queued]:
                LOGGER.debug(f"Stopping running job {job_id}")
                self._stop_airflow_job(user_id, job_id)
                LOGGER.info(f"Stopped running job {job_id}.")

            self.files_service.delete_complete_job(user_id, job_id)  # delete data on file system
            os.remove(self.get_dag_path(job.dag_filename))  # delete dag file
            self.airflow.delete_dag(job_id)  # delete from airflow database
            self.db.delete(job)  # delete from our job database
            self.db.commit()
            LOGGER.info(f"Job {job_id} completely deleted.")

            return {
                "status": "success",
                "code": 204
            }

        except Exception as exp:
            return ServiceException(500, user_id, str(exp), links=[]).to_dict()

    @rpc
    def get_all(self, user_id: str) -> dict:
        """The request will ask the back-end to get all available jobs for the given user.

        Arguments:
            user_id {str} -- The identifier of the user
        """
        try:
            jobs = self.db.query(Job.id).filter_by(user_id=user_id).order_by(Job.created_at).all()
            for job in jobs:
                self._update_job_status(job.id)

            jobs = self.db.query(Job).filter_by(user_id=user_id).order_by(Job.created_at).all()
            return {
                "status": "success",
                "code": 200,
                "data": {
                    "jobs": JobShortSchema(many=True).dump(jobs),
                    "links": []
                }
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1jobs/get"]).to_dict()

    @rpc
    def create(self, user_id: str, **job_args) -> dict:
        """The request will ask the back-end to create a new job using the description send in the request body.

        Arguments:
            user_id {str} -- The identifier of the user
            job_args {dict} -- The information needed to create a job
        """
        try:
            LOGGER.debug("Start creating job...")
            process = job_args.pop("process")
            process_graph_id = process["id"] if "id" in process else str(uuid4())
            process_response = self.processes_service.put_user_defined(
                user_id=user_id, process_graph_id=process_graph_id, **process)
            if process_response["status"] == "error":
                return process_response
            LOGGER.info(f"ProcessGraph {process_graph_id} created")

            job_args["process_graph_id"] = process_graph_id
            job_args["user_id"] = user_id
            job = JobCreateSchema().load(job_args)
            self.db.add(job)
            self.db.commit()
            job_id = str(job.id)

            self.files_service.setup_jobs_result_folder(user_id=user_id, job_id=job_id)

            self.dag_writer.write_and_move_job(job_id=job_id, user_name=user_id,
                                               process_graph_json=process["process_graph"],
                                               job_data=self.get_job_folder(user_id, job_id),
                                               vrt_only=True, add_delete_sensor=True)
            job.dag_filename = f"dag_{job_id}.py"
            self.db.add(job)
            self.db.commit()
            LOGGER.info(f"Dag file created for job {job_id}")

            return {
                "status": "success",
                "code": 201,
                "headers": {
                    "Location": "jobs/" + job_id,
                    "OpenEO-Identifier": job_id
                }
            }

        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1jobs/post"]).to_dict()

    @rpc
    def process(self, user_id: str, job_id: str) -> dict:
        """The request will ask the back-end to start the processing of the given job.
        The job needs to exist on the back-end and must not already be queued or running.

        Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the job
        """
        try:
            job = self.db.query(Job).filter_by(id=job_id).first()
            valid, response = self.authorize(user_id, job_id, job)
            if not valid:
                return response

            self._update_job_status(job_id=job_id)
            if job.status in [JobStatus.queued, JobStatus.running]:
                return ServiceException(400, user_id, f"Job {job_id} is already {job.status}. Processing must be "
                                                      f"canceled before restart.", links=[]).to_dict()

            trigger_worked = self.airflow.trigger_dag(job_id)
            if not trigger_worked:
                return ServiceException(500, user_id, f"Job {job_id} could not be started.", links=[]).to_dict()

            self._update_job_status(job_id=job_id)
            LOGGER.info(f"Processing successfully started for job {job_id}")
            return {
                "status": "success",
                "code": 202,
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp), links=[]).to_dict()

    @rpc
    def estimate(self, user_id: str, job_id: str) -> dict:
        """
        Basic function to return default information about processing costs on back-end.
        """

        default_out = {
            "costs": 0,
            "duration": "null",
            "download_included": True,
            "expires": "null"
        }

        return {
            "status": "success",
            "code": 200,
            "data": default_out
        }

    @rpc
    def cancel_processing(self, user_id: str, job_id: str):
        """The request will ask the back-end to cancel the processing of the given job.
        This will stop the processing if the job is currently queued or running and remove all not persistent result.
        The job itself and results are kept.

        Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the job
        """
        try:
            # TODO handle costs (stop it)
            LOGGER.debug(f"Start canceling job {job_id}")
            job = self.db.query(Job).filter_by(id=job_id).first()
            valid, response = self.authorize(user_id, job_id, job)
            if not valid:
                return response

            self._update_job_status(job_id=job_id)
            if job.status in [JobStatus.running, JobStatus.queued]:
                LOGGER.debug(f"Stopping running job {job_id}...")
                self._stop_airflow_job(user_id, job_id)
                LOGGER.info(f"Stopped running job {job_id}.")

                results_exists = self.files_service.delete_job_without_results(user_id, job_id)
                if job.status == JobStatus.running and results_exists:
                    self._update_job_status(job_id, JobStatus.canceled)
                else:
                    self._update_job_status(job_id, JobStatus.created)
                self.db.commit()
                LOGGER.info(f"Job {job_id} has not the status {job.status}.")

            LOGGER.info(f"Job {job_id} canceled.")
            return {
                "status": "success",
                "code": 204
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1jobs~1{job_id}~1results/delete"]).to_dict()

    @rpc
    def get_results(self, user_id: str, job_id: str):
        """The request will ask the back-end to get the location where the results of the given job can be retrieved.
        This only works if the job is in state finished.

        Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the job
        """
        try:
            self._update_job_status(job_id=job_id)
            job = self.db.query(Job).filter_by(id=job_id).first()
            valid, response = self.authorize(user_id, job_id, job)
            if not valid:
                return response

            if job.status == JobStatus.error:
                return ServiceException(424, user_id, job.error, internal=False)  # TODO store error!

            if job.status == JobStatus.canceled:
                return ServiceException(400, user_id, f"Job {job_id} was canceled.")

            if job.status in [JobStatus.created, JobStatus.queued, JobStatus.running]:
                return JobNotFinished(400, user_id, job_id, internal=False)

            # Job status is "finished"
            output = self.files_service.get_job_output(user_id=user_id, job_id=job_id)
            if output["status"] == "error":
                return output

            # file list could be retrieved
            job_data = JobResultsSchema().dump(job)
            job_data["link"] = [{
                "href": self._get_download_url(f),
                "type": "image/tiff",
            } for f in output['data']['file_list']]

            return {
                "status": "success",
                "code": 200,
                "headers": {
                    "Expires": "not given",
                    "OpenEO-Costs": 0
                },
                "data": job_data
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp), links=[]).to_dict()

    def _get_download_url(self, public_path: str):
        """ This will create the public url where result data can be downloaded

        Arguments:
            public_path {str} -- local result path

        Returns:
            str -- Complete url path
        """
        return os.path.join(os.environ.get("GATEWAY_URL"), "downloads", public_path)

    @staticmethod
    def authorize(user_id: str, job_id: str, job: Job) -> Tuple[bool, Optional[dict]]:
        """Return Exception if given Job does not exist or User is not allowed to access this Job.

        Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the job
            job {ProcessGraph} -- The Job object for the given job_id
        """
        if job is None:
            return False, ServiceException(400, user_id, f"The job with id '{job_id}' does not exist.",
                                           internal=False, links=["#tag/Job-Management/paths/~1data/get"]).to_dict()

        # TODO: Permission (e.g admin)
        if job.user_id != user_id:
            return False, ServiceException(401, user_id, "You are not allowed to access this resource.",
                                           internal=False, links=["#tag/Job-Management/paths/~1data/get"]).to_dict()

        LOGGER.info(f"User is authorized to access job {job_id}.")
        return True, None

    def _update_job_status(self, job_id: str, manual_status: JobStatus = None) -> None:
        """Updates the job status.

        Whenever the job status is updated this method should be used to ensure the status_updated_at column is properly
        set!
        Either a status can be set manually or it is retrieved from airflow.

        Arguments:
            job_id {str} -- The id of the job

        Keyword Arguments:
            manual_status {JobStatus} -- The JobStatus to set for the job
        """
        job = self.db.query(Job).filter_by(id=job_id).first()
        if manual_status:
            job.status = manual_status
        else:
            new_status, execution_time = self.airflow.check_dag_status(job_id)
            if new_status and (not job.status
                               or job.status in [JobStatus.queued, JobStatus.running, JobStatus.error]
                               # Job status created or canceled, when job is canceled:
                               # > state in airflow set to failed though locally is stored as created or canceled
                               # > the state should only be updated if there was a new dag run since the canceled one
                               # - all times are stored in UTC
                               or (execution_time and job.status_updated_at < execution_time)):
                job.status = new_status

        job.status_updated_at = datetime.utcnow()
        self.db.commit()
        LOGGER.debug(f"Job Status of job {job_id} is {job.status}")

    def get_job_folder(self, user_id: str, job_id: str) -> str:
        """Get path to specific job folder of a user.

        Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the job

        Returns:
            str -- The complete path to the job folder on the file system
        """
        return os.path.join(os.environ["JOB_DATA"], user_id, "jobs", job_id)

    def get_dag_path(self, dag_id: str) -> str:
        """Get the complete path on the file system of a dag file.

        Arguments:
            dag_id {str} -- The identifier / filename of the dag

        Returns:
            str -- Absolute location of the dag on the file system
        """
        return os.path.join(os.environ.get("AIRFLOW_DAGS"), dag_id)

    def _stop_airflow_job(self, user_id: str, job_id: str) -> None:
        """This triggers the airflow observer to set all running task to failed.
        This will stop any successor tasks to start but it will not stop the currently running task.

        Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the job
        """
        self.files_service.upload_stop_job_file(user_id, job_id)

        # Wait till job is stopped
        job_stopped = False
        while not job_stopped:
            LOGGER.info("Waiting for airflow sensor to detect STOP file...")
            sleep(self.check_stop_interval)
            job_stopped = self.airflow.check_dag_status(job_id) != JobStatus.running
