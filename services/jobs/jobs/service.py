""" Job Management """

import logging
import os
from time import sleep
from uuid import uuid4

from eodc_openeo_bindings.job_writer.dag_writer import AirflowDagWriter
from nameko.rpc import rpc, RpcProxy
from nameko_sqlalchemy import DatabaseSession

from .dependencies.airflow_conn import Airflow
from .models import Base, Job, JobStatus
from .schema import JobSchema, JobSchemaFull, JobSchemaShort, JobCreateSchema

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
    check_stop_interval = 10

    @rpc
    def get(self, user_id: str, job_id: str) -> dict:
        """The request will ask the back-end to get the job using the job_id.

        Keyword Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the job
        """
        try:
            self._update_job_status(job_id=job_id)
            job = self.db.query(Job).filter_by(id=job_id).first()

            valid, response = self.authorize(user_id, job_id, job)
            if not valid:
                return response

            response = self.processes_service.get_user_defined(user_id, job.process_graph_id)
            if response["status"] == "error":
                return response
            job.process = response["data"]["process_graph"]

            return {
                "status": "success",
                "code": 200,
                "data": JobSchemaFull().dump(job)
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp), links=[]).to_dict()

    @rpc
    def modify(self, user_id: str, job_id: str, **job_args) -> dict:
        """The request will ask the back-end to modify the job with the given job_id.

        Keyword Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the job
        """
        try:
            self._update_job_status(job_id=job_id)
            job = self.db.query(Job).filter_by(id=job_id).first()
            valid, response = self.authorize(user_id, job_id, job)
            if not valid:
                return response

            if job.status in [JobStatus.queued, JobStatus.running]:
                return JobLocked(400, user_id, f"Job {job_id} is currently {job.status} and cannot be modified",
                                 links=[]).to_dict()

            if job_args.get("process_graph", None):
                process_graph_args = job_args.pop('process_graph')
                process_graph_id = process_graph_args["id"] if "id" in process_graph_args else str(uuid4())
                process_response = self.processes_service.put_user_defined(
                    user_id=user_id, process_graph_id=process_graph_id, **process_graph_args)
                if process_response["status"] == "error":
                    return process_response
                job_args["process_graph_id"] = process_graph_id

            # Maybe there is a better option to do this update? e.g. using marshmallow schemas?
            job.title = job_args.get("title", job.title)
            job.process_graph_id = job_args.get("process_graph_id", job.process_graph_id)
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
        """The request will ask the back-end to delete the job with the given job_id.

        Keyword Arguments:
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
            # JobStatus should never be queued -> does not exist for a dag in airflow
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

        Keyword Arguments:
            user_id {str} -- The identifier of the user
        """
        try:
            # TODO status update should be done separately
            jobs = self.db.query(Job.id).filter_by(user_id=user_id).order_by(Job.created_at).all()
            for job in jobs:
                self._update_job_status(job.id)
            jobs = self.db.query(Job).filter_by(user_id=user_id).order_by(Job.created_at).all()

            return {
                "status": "success",
                "code": 200,
                "data": {
                    "jobs": JobSchema(many=True).dump(jobs),
                    "links": []
                }
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1jobs/get"]).to_dict()

    @rpc
    def create(self, user_id: str, **job_args) -> dict:
        """The request will ask the back-end to create a new job using the description send in the request body.

        Keyword Arguments:
            user_id {str} -- The identifier of the user
            job_args {dict} -- The information needed to create a job
        """
        try:
            LOGGER.debug("Start creating job")
            process = job_args.pop("process")
            process_graph_id = process["id"] if "id" in process else str(uuid4())
            process_response = self.processes_service.put_user_defined(
                user_id=user_id, process_graph_id=process_graph_id, **process)
            if process_response["status"] == "error":
                return process_response
            LOGGER.debug("ProcessGraph created")

            job_args["process_graph_id"] = process_graph_id
            job_args["user_id"] = user_id
            job = JobCreateSchema().load(job_args)
            self.db.add(job)
            self.db.commit()
            job_id = str(job.id)

            self.files_service.setup_jobs_result_folder(user_id=user_id, job_id=job_id)

            job_folder = self.get_job_folder(user_id, job_id)
            writer = AirflowDagWriter(job_id, user_id, process_graph_json=process["process_graph"], job_data=job_folder,
                                      vrt_only=True, add_delete_sensor=True)
            writer.write_and_move_job()
            job.dag_filename = writer.file_handler.filepath
            self.db.commit()
            LOGGER.debug("Dag file created")

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
        try:
            job = self.db.query(Job).filter_by(id=job_id).first()
            valid, response = self.authorize(user_id, job_id, job)
            if not valid:
                return response

            if not self.airflow.trigger_dag(job_id):
                return ServiceException(500, user_id, f"Job {job_id} could not be started.", links=[]).to_dict()

            self._update_job_status(job_id=job_id)
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
        try:
            raise Exception("Not implemented yet!")
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1jobs~1{job_id}~1results/delete"]).to_dict()

    @rpc
    def get_results(self, user_id: str, job_id: str):
        try:
            self._update_job_status(job_id=job_id)
            job = self.db.query(Job).filter_by(id=job_id).first()
            if job.status != JobStatus.finished:
                raise Exception(response)  # NB code proper response "JobNotFinished"

            valid, response = self.authorize(user_id, job_id, job)
            if not valid:
                raise Exception(response)

            output = self.files_service.get_job_output(user_id=user_id, job_id=job_id)

            if output['status'] == 'success':
                job_data = JobSchemaShort().dump(job).data
                job_data['links'] = []
                for filepath in output['data']['file_list']:
                    filename = os.path.join(os.environ.get("GATEWAY_URL"),
                                            "downloads", user_id, job_id, filepath.split(os.path.sep)[-1])
                    job_data['links'].append({
                        "href": filename,
                        "type": "image/tiff"
                    }
                    )

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
            return ServiceException(500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1jobs~1{job_id}~1results/get"]).to_dict()

    @staticmethod
    def authorize(user_id: str, job_id: str, job: Job):
        """Return Exception if given Job does not exist or User is not allowed to access this Job.

        Keyword Arguments:
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

    def _update_job_status(self, job_id: str):
        """
        Get job status from airflow db and updates jobs db.
        """
        new_status = self.airflow.check_dag_status(job_id)
        if new_status:
            job = self.db.query(Job).filter_by(id=job_id).first()
            job.status = new_status
            self.db.commit()

    def get_job_folder(self, user_id: str, job_id: str) -> str:
        return os.path.join(os.environ["JOB_DATA"], user_id, "jobs", job_id)

    def get_dag_path(self, dag_id: str) -> str:
        return os.path.join(os.environ.get("AIRFLOW_DAGS"), dag_id)

    def _stop_airflow_job(self, user_id: str, job_id: str):
        # This should trigger the airflow observer to set all running task to failed.
        # This will not stop the currently running task
        self.files_service.upload_stop_job_file(user_id, job_id)

        # Wait till job is stopped
        job_stopped = False
        while not job_stopped:
            LOGGER.info(f"Waiting for airflow sensor to detect STOP file...")
            sleep(self.check_stop_interval)
            job_stopped = self.airflow.check_dag_status(job_id) != JobStatus.running
