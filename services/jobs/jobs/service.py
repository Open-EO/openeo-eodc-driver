""" Job Management """
import json
import logging
import os
import random
import shutil
import string
import threading
from collections import namedtuple
from datetime import datetime
from time import sleep
from typing import Any, Dict, Optional

from dynaconf import settings
from eodc_openeo_bindings.job_writer.dag_writer import AirflowDagWriter
from nameko.rpc import RpcProxy, rpc
from nameko_sqlalchemy import DatabaseSession

from .dependencies.airflow_conn import AirflowRestConnectionProvider
from .dependencies.settings import initialise_settings
from .exceptions import JobLocked, JobNotFinished, ServiceException
from .models import Base, Job, JobStatus
from .schema import JobCreateSchema, JobFullSchema, JobResultsBaseSchema, JobShortSchema

service_name = "jobs"
LOGGER = logging.getLogger('standardlog')
initialise_settings()


class JobService:
    """Management of batch processing tasks (jobs) and their results.
    """

    name = service_name
    db = DatabaseSession(Base)
    processes_service = RpcProxy("processes")
    files_service = RpcProxy("files")
    airflow = AirflowRestConnectionProvider()
    dag_writer = AirflowDagWriter()
    check_stop_interval = 5  # should be similar or smaller than Airflow sensor's poke interval

    @rpc
    def get(self, user: Dict[str, Any], job_id: str) -> dict:
        """The request will ask the back-end to get the job using the job_id.

        Arguments:
            user_id {Dict[str, Any]} -- The user object
            job_id {str} -- The id of the job
        """
        try:
            job = self.db.query(Job).filter_by(id=job_id).first()
            response = self.authorize(user["id"], job_id, job)
            if isinstance(response, ServiceException):
                return response.to_dict()

            self._update_job_status(job_id=job_id)
            process_response = self.processes_service.get_user_defined(user, job.process_graph_id)
            if process_response["status"] == "error":
                return process_response
            job.process = process_response["data"]

            return {
                "status": "success",
                "code": 200,
                "data": JobFullSchema().dump(job)
            }
        except Exception as exp:
            return ServiceException(500, user["id"], str(exp), links=[]).to_dict()

    @rpc
    def modify(self, user: Dict[str, Any], job_id: str, **job_args: Any) -> dict:
        """The request will ask the back-end to modify the job with the given job_id.

        Arguments:
            user {Dict[str, Any]} -- The user object
            job_id {str} -- The id of the job
            job_args {Dict[str, Any]} -- The job arguments to be moified
        """
        try:
            job = self.db.query(Job).filter_by(id=job_id).first()
            response = self.authorize(user["id"], job_id, job)
            if isinstance(response, ServiceException):
                return response.to_dict()

            self._update_job_status(job_id=job_id)
            if job.status in [JobStatus.queued, JobStatus.running]:
                return JobLocked(400, user["id"], f"Job {job_id} is currently {job.status} and cannot be modified",
                                 links=[]).to_dict()

            if job_args.get("process", None):

                # handle processes db
                process_graph_args = job_args.pop('process')
                process_graph_id = process_graph_args["id"] if "id" in process_graph_args \
                    else self.generate_alphanumeric_id()
                process_response = self.processes_service.put_user_defined(
                    user=user, process_graph_id=process_graph_id, **process_graph_args)
                if process_response["status"] == "error":
                    return process_response
                job.process_graph_id = process_graph_id

                # Get all processes
                process_response = self.processes_service.get_all_predefined()
                if process_response["status"] == "error":
                    return process_response
                backend_processes = process_response["data"]["processes"]

                # handle dag file (remove and recreate it) - only needs to be updated if process graph changes
                os.remove(self.get_dag_path(job.dag_filename))
                self.dag_writer.write_and_move_job(job_id=job_id, user_name=user["id"],
                                                   process_graph_json=process_graph_args,
                                                   job_data=self.get_job_folder(user["id"], job_id),
                                                   vrt_only=True, add_delete_sensor=True,
                                                   process_defs=backend_processes)

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
            return ServiceException(500, user["id"], str(exp),
                                    links=[]).to_dict()

    @rpc
    def delete(self, user: Dict[str, Any], job_id: str) -> dict:
        """The request will ask the back-end to completely delete the job with the given job_id.
        This will stop the job if it is currently queued or running, remove the job itself and all results.

        Arguments:
            user {Dict[str, Any]} -- The user object
            job_id {str} -- The id of the process graph
        """
        # TODO handle costs (stop it)
        try:
            LOGGER.debug(f"Start deleting job {job_id}")
            job = self.db.query(Job).filter_by(id=job_id).first()
            response = self.authorize(user["id"], job_id, job)
            if isinstance(response, ServiceException):
                return response.to_dict()

            self._update_job_status(job_id=job_id)
            if job.status in [JobStatus.running, JobStatus.queued]:
                LOGGER.debug(f"Stopping running job {job_id}")
                self._stop_airflow_job(user["id"], job_id)
                LOGGER.info(f"Stopped running job {job_id}.")

            self.files_service.delete_complete_job(user_id=user["id"], job_id=job_id)  # delete data on file system
            os.remove(self.get_dag_path(job.dag_filename))  # delete dag file
            self.airflow.delete_dag(job_id=job_id)  # delete from airflow database
            self.db.delete(job)  # delete from our job database
            self.db.commit()
            LOGGER.info(f"Job {job_id} completely deleted.")

            return {
                "status": "success",
                "code": 204
            }

        except Exception as exp:
            return ServiceException(500, user["id"], str(exp), links=[]).to_dict()

    @rpc
    def get_all(self, user: Dict[str, Any]) -> dict:
        """The request will ask the back-end to get all available jobs for the given user.

        Arguments:
            user {Dict[str, Any]} -- The user object
        """
        try:
            jobs = self.db.query(Job.id).filter_by(user_id=user["id"]).order_by(Job.created_at).all()
            for job in jobs:
                self._update_job_status(job.id)

            jobs = self.db.query(Job).filter_by(user_id=user["id"]).order_by(Job.created_at).all()
            return {
                "status": "success",
                "code": 200,
                "data": {
                    "jobs": JobShortSchema(many=True).dump(jobs),
                    "links": []
                }
            }
        except Exception as exp:
            return ServiceException(500, user["id"], str(exp),
                                    links=["#tag/Job-Management/paths/~1jobs/get"]).to_dict()

    @rpc
    def create(self, user: Dict[str, Any], **job_args: Any) -> dict:
        """The request will ask the back-end to create a new job using the description send in the request body.

        Arguments:
            user {Dict[str, Any]} -- The user object
            job_args {Dict[str, Any]} -- The information needed to create a job
        """
        try:
            LOGGER.debug("Start creating job...")
            vrt_flag = True 
            if 'vrt_flag' in job_args.keys():
                vrt_flag = job_args.pop("vrt_flag")
            process = job_args.pop("process")
            process_graph_id = process["id"] if "id" in process else self.generate_alphanumeric_id()
            process_response = self.processes_service.put_user_defined(
                user=user, process_graph_id=process_graph_id, **process)
            if process_response["status"] == "error":
                return process_response
            LOGGER.info(f"ProcessGraph {process_graph_id} created")

            job_args["process_graph_id"] = process_graph_id
            job_args["user_id"] = user["id"]
            job = JobCreateSchema().load(job_args)
            self.db.add(job)
            self.db.commit()
            job_id = str(job.id)

            _ = self.files_service.setup_jobs_result_folder(user_id=user["id"], job_id=job_id)

            # Get all processes
            process_response = self.processes_service.get_all_predefined()
            if process_response["status"] == "error":
                return process_response
            backend_processes = process_response["data"]["processes"]
            self.dag_writer.write_and_move_job(job_id=job_id, 
                                               user_name=user["id"],
                                               process_graph_json=process,
                                               job_data=self.get_job_folder(user["id"], job_id),
                                               vrt_only=vrt_flag, 
                                               add_delete_sensor=True,
                                               add_parallel_sensor=True,
                                               process_defs=backend_processes)
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
            return ServiceException(500, user["id"], str(exp),
                                    links=["#tag/Job-Management/paths/~1jobs/post"]).to_dict()

    @rpc
    def process(self, user: Dict[str, Any], job_id: str) -> dict:
        """The request will ask the back-end to start the processing of the given job.
        The job needs to exist on the back-end and must not already be queued or running.

        Arguments:
            user {Dict[str, Any]} -- The user object
            job_id {str} -- The id of the job
        """
        try:
            job = self.db.query(Job).filter_by(id=job_id).first()
            response = self.authorize(user["id"], job_id, job)
            if isinstance(response, ServiceException):
                return response.to_dict()

            self._update_job_status(job_id=job_id)
            if job.status in [JobStatus.queued, JobStatus.running]:
                return ServiceException(400, user["id"], f"Job {job_id} is already {job.status}. Processing must be "
                                                         f"canceled before restart.", links=[]).to_dict()

            trigger_worked = self.airflow.trigger_dag(job_id=job_id)
            if not trigger_worked:
                return ServiceException(500, user["id"], f"Job {job_id} could not be started.", links=[]).to_dict()

            self._update_job_status(job_id=job_id)
            LOGGER.info(f"Processing successfully started for job {job_id}")
            return {
                "status": "success",
                "code": 202,
            }
        except Exception as exp:
            return ServiceException(500, user["id"], str(exp), links=[]).to_dict()

    @rpc
    def process_sync(self, user: Dict[str, Any], **job_args: Any) -> dict:
        """The request will ask the back-end to start the processing of the given job.
        The job needs to exist on the back-end and must not already be queued or running.

        Arguments:
            user {Dict[str, Any]} -- The user object
            job_args {dict} -- The information needed to create a job
        """

        TypeMap = namedtuple('TypeMap', 'file_extension content_type')
        type_map = {
            'Gtiff': TypeMap('tif', 'image/tiff'),
            'png': TypeMap('png', 'image/png'),
            'jpeg': TypeMap('jpeg', 'image/jpeg'),
        }

        try:
            # TODO: implement a check that the job qualifies for sync-processing
            # it has to be a "small" job, e.g. constriants for timespan and bboux, but also on spatial resolution

            # Create Job
            LOGGER.info("Creating job for sync processing.")
            job_args['vrt_flag'] = False
            response_create = self.create(user=user, **job_args)
            if response_create['status'] == 'error':
                return response_create

            # Start processing
            job_id = response_create["headers"]["Location"].split('/')[-1]
            job = self.db.query(Job).filter_by(id=job_id).first()
            response_process = self.process(user=user, job_id=job_id)
            if response_process['status'] == 'error':
                return response_process

            LOGGER.info(f"Job {job_id} is running.")
            self._update_job_status(job_id=job_id)
            while job.status in [JobStatus.queued, JobStatus.running]:
                sleep(10)
                self._update_job_status(job_id=job_id)
            if job.status in [JobStatus.error, JobStatus.canceled]:
                msg = f"Job {job_id} has status: {job.status}."
                return ServiceException(400, user["id"], msg, links=[]).to_dict()

            LOGGER.info(f"Job {job_id} has been processed.")
            self.airflow.unpause_dag(job_id=job_id, unpause=False)  # just to hide from view on default Airflow web view
            response_files = self.files_service.get_job_output(user_id=user["id"], job_id=job_id)
            if response_files["status"] == "error":
                LOGGER.info(f"Could not retrieve output of Job {job_id}.")
                return response_files

            filepath = response_files['data']['file_list'][0]
            fmt = self.map_output_format(filepath.split('.')[-1])

            # Copy directory to tmp location
            job_folder = self.files_service.setup_jobs_result_folder(user_id=user["id"], job_id=job_id) \
                .replace('/result', '')
            job_tmp_folder = os.path.join(settings.SYNC_RESULTS_FOLDER, job_id)
            shutil.copytree(job_folder, job_tmp_folder)
            filepath = filepath.replace(job_folder, job_tmp_folder)

            # Remove job data (sync jobs must not be stored)
            response_delete = self.delete(user=user, job_id=job_id)
            if response_delete["status"] == "error":
                LOGGER.info(f"Could not delete Job {job_id}.")
                return response_delete

            # Schedule async deletion of tmp folder
            threading.Thread(target=self._delayed_delete, args=(job_tmp_folder, )).start()

            return {
                "status": "success",
                "code": 200,
                "headers": {
                    "Content-Type": type_map[fmt].content_type,
                    "OpenEO-Costs": 0,
                },
                "file": filepath
            }

        except Exception as exp:
            return ServiceException(500, user["id"], str(exp), links=[]).to_dict()

    @rpc
    def estimate(self, user: Dict[str, Any], job_id: str) -> dict:
        """
        Basic function to return default information about processing costs on back-end.

        Arguments:
            user_id {Dict[str, Any]} -- The user object
            job_id {str} -- The id of the job
        """

        default_out = {
            "costs": 0,  # for now no costs are calculated
        }

        LOGGER.info("Costs estimated.")
        return {
            "status": "success",
            "code": 200,
            "data": default_out
        }

    @rpc
    def cancel_processing(self, user: Dict[str, Any], job_id: str) -> dict:
        """The request will ask the back-end to cancel the processing of the given job.
        This will stop the processing if the job is currently queued or running and remove all not persistent result.
        The job itself and results are kept.

        Arguments:
            user_id {Dict[str, Any]} -- The user object
            job_id {str} -- The id of the job
        """
        try:
            # TODO handle costs (stop it)
            LOGGER.debug(f"Start canceling job {job_id}")
            job = self.db.query(Job).filter_by(id=job_id).first()
            response = self.authorize(user["id"], job_id, job)
            if isinstance(response, ServiceException):
                return response.to_dict()

            self._update_job_status(job_id=job_id)
            if job.status in [JobStatus.running, JobStatus.queued]:
                LOGGER.debug(f"Stopping running job {job_id}...")
                self._stop_airflow_job(user["id"], job_id)
                LOGGER.info(f"Stopped running job {job_id}.")

                results_exists = self.files_service.delete_job_without_results(user["id"], job_id)
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
            return ServiceException(500, user["id"], str(exp),
                                    links=["#tag/Job-Management/paths/~1jobs~1{job_id}~1results/delete"]).to_dict()

    @rpc
    def get_results(self, user: Dict[str, Any], job_id: str, api_spec: dict) -> dict:
        """The request will ask the back-end to get the location where the results of the given job can be retrieved.
        This only works if the job is in state finished.

        Arguments:
            user {Dict[str, Any]} -- The user object
            job_id {str} -- The id of the job
            api_spec {dict} -- OpenAPI Specification (needed for STAC Version)
        """
        try:
            job = self.db.query(Job).filter_by(id=job_id).first()
            response = self.authorize(user["id"], job_id, job)
            if isinstance(response, ServiceException):
                return response.to_dict()
            self._update_job_status(job_id=job_id)
            job = self.db.query(Job).filter_by(id=job_id).first()

            if job.status == JobStatus.error:
                return ServiceException(424, user["id"], job.error, internal=False).to_dict()  # TODO store error!

            if job.status == JobStatus.canceled:
                return ServiceException(400, user["id"], f"Job {job_id} was canceled.", internal=False).to_dict()

            if job.status in [JobStatus.created, JobStatus.queued, JobStatus.running]:
                return JobNotFinished(400, user["id"], job_id, internal=False).to_dict()

            # Job status is "finished"
            output = self.files_service.get_job_output(user_id=user["id"], job_id=job_id)
            if output["status"] == "error":
                return output
            file_list = output["data"]["file_list"]
            metadata_file = output["data"]["metadata_file"]

            # # Add additional metadata from json
            with open(metadata_file) as f:
                metadata = json.load(f)

            job.assets = [{
                "href": self._get_download_url(f),
                "name": os.path.basename(f)
            } for f in file_list]

            # TODO fix links
            job.links = [{"href": "https://openeo.eodc.eu/v1.0/collections", "rel": "self"}]
            job.stac_version = api_spec["info"]["stac_version"]

            # file list could be retrieved
            job_data = JobResultsBaseSchema().dump(job)
            job_data.update(metadata)
            # Fix 'type' field, must always be 'Feature'
            if job_data['type'] != "Feature":
                job_data['type'] = "Feature"

            return {
                "status": "success",
                "code": 200,
                "headers": {
                    "Expires": "not given",
                    "OpenEO-Costs": 0
                },
                "data": job_data,
            }
        except Exception as exp:
            return ServiceException(500, user["id"], str(exp), links=[]).to_dict()

    def _get_download_url(self, public_path: str) -> str:
        """ This will create the public url where result data can be downloaded

        Arguments:
            public_path {str} -- local result path

        Returns:
            str -- Complete url path
        """

        if settings.ENV_FOR_DYNACONF.lower() == "development":
            download_url = os.path.join(settings.GATEWAY_URL, settings.OPENEO_VERSION, "downloads", public_path)
        else:
            download_url = os.path.join(settings.DNS_URL, "downloads", public_path)

        return download_url

    @staticmethod
    def authorize(user_id: str, job_id: str, job: Job) -> Optional[ServiceException]:
        """Return Exception if given Job does not exist or User is not allowed to access this Job.

        Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the job
            job {ProcessGraph} -- The Job object for the given job_id
        """
        if job is None:
            return ServiceException(400, user_id, f"The job with id '{job_id}' does not exist.",
                                    internal=False, links=["#tag/Job-Management/paths/~1data/get"])

        # TODO: Permission (e.g admin)
        if job.user_id != user_id:
            return ServiceException(401, user_id, f"You are not allowed to access the job {job_id}.",
                                    internal=False, links=["#tag/Job-Management/paths/~1data/get"])

        LOGGER.info(f"User is authorized to access job {job_id}.")
        return None

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
                               or job.status in [JobStatus.created,
                                                 JobStatus.queued,
                                                 JobStatus.running,
                                                 JobStatus.error]
                               # Job status created or canceled, when job is canceled:
                               # > state in airflow set to failed though locally is stored as created or canceled
                               # > the state should only be updated if there was a new dag run since the canceled one
                               # - all times are stored in UTC
                               or (execution_time and job.status_updated_at.replace(tzinfo=None) < execution_time)):
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
        return os.path.join(settings.JOB_DATA, user_id, "jobs", job_id)

    def get_dag_path(self, dag_id: str) -> str:
        """Get the complete path on the file system of a dag file.

        Arguments:
            dag_id {str} -- The identifier / filename of the dag

        Returns:
            str -- Absolute location of the dag on the file system
        """
        return os.path.join(settings.AIRFLOW_DAGS, dag_id)

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

    @staticmethod
    def map_output_format(output_format: str) -> str:
        out_map = [(['Gtiff', 'GTiff', 'tif', 'tiff'], 'Gtiff'),
                   (['jpg', 'jpeg'], 'jpeg'),
                   (['png'], 'png')
                   ]
        for synonyms, out_name in out_map:
            if output_format in synonyms:
                return out_name
        raise ValueError('{} is not a supported output format'.format(output_format))

    def _delayed_delete(self, folder_path: str) -> None:
        """Deletes a folder corresponding to a job, after having waiting for a sufficient amount of time.
        
        Arguments:
            folder_path {str} -- The full path to the folder to be deleted
        """

        # Wait n minutes (allow for enough time to stream file(s) to user)
        sleep(settings.SYNC_DEL_DELAY)
        # Remove tmp folder
        shutil.rmtree(folder_path)        

    def generate_alphanumeric_id(self, k: int = 16) -> str:
        """
        Generates a random alpha numeric value.
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
