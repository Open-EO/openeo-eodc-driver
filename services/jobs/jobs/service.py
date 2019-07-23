""" Job Management """

import os
from nameko.rpc import rpc, RpcProxy
from nameko_sqlalchemy import DatabaseSession

from .models import Base, Job
from .schema import JobSchema, JobSchemaFull
# from .exceptions import BadRequest, Forbidden, APIConnectionError
# from .dependencies.task_parser import TaskParser
# from .dependencies.validator import Validator
# from .dependencies.api_connector import APIConnector
from .dependencies.template_controller import TemplateController
from .models import JobStatus
from .dependencies.write_airflow_dag import WriteAirflowDag
from .dependencies.airflow_conn import Airflow


service_name = "jobs"


class ServiceException(Exception):
    """ServiceException raises if an exception occured while processing the
    request. The ServiceException is mapping any exception to a serializable
    format for the API gateway.
    """

    def __init__(self, code: int, user_id: str, msg: str, internal: bool=True, links: list=None):
        if not links:
            links = []

        self._service = service_name
        self._code = code
        self._user_id = user_id
        self._msg = msg
        self._internal = internal
        self._links = links

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
    def __init__(self, code: int, user_id: str, msg: str, internal: bool=True, links: list=None):
        super(JobLocked, self).__init__(code, user_id, msg, internal, links)


class JobService:
    """Management of batch processing tasks (jobs) and their results.
    """

    name = service_name
    db = DatabaseSession(Base)
    process_graphs_service = RpcProxy("process_graphs")
    data_service = RpcProxy("data")
    # api_connector = APIConnector()
    template_controller = TemplateController()
    airflow = Airflow()

    @rpc
    def get(self, user_id: str, job_id: str):
        """The request will ask the back-end to get the job using the job_id.

        Keyword Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the job
        """
        try:
            job = self.db.query(Job).filter_by(id=job_id).first()

            valid, response = self.authorize(user_id, job_id, job)
            if not valid:
                return response

            response = self.process_graphs_service.get(user_id, job.process_graph_id)
            if response["status"] == "error":
                return response

            job.process_graph = response["data"]["process_graph"]
            return {
                "status": "success",
                "code": 200,
                "data": JobSchemaFull().dump(job).data
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1jobs~1{job_id}/get"]).to_dict()

    @rpc
    def modify(self, user_id: str, job_id: str, **job_args):
        """The request will ask the back-end to modify the job with the given job_id.

        Keyword Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the job
        """
        try:
            job = self.db.query(Job).filter_by(id=job_id).first()
            valid, response = self.authorize(user_id, job_id, job)
            if not valid:
                return response

            if job.status in [JobStatus.queued, JobStatus.running]:
                msg = "Job {0} is currently {1} and cannot be modified".format(job_id, job.status)
                return JobLocked(400, user_id, msg, links=["jobs/" + job_id])

            process_graph_id = None
            if job_args.get("process_graph", None):
                process_response = self.process_graphs_service.create(
                    user_id=user_id,
                    **{"process_graph": job_args.pop('process_graph')})

                if process_response["status"] == "error":
                    return process_response
                process_graph_id = process_response["service_data"]

            job.update(process_graph_id, **job_args)
            self.db.merge(job)
            self.db.commit()

            return {
                    "status": "success",
                    "code": 204
                }

        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1jobs~1{job_id}/patch"]).to_dict()

    @rpc
    def delete(self, user_id: str, job_id: str):
        """The request will ask the back-end to delete the job with the given job_id.

        Keyword Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the process graph
        """
        try:
            job = self.db.query(Job).filter_by(id=job_id).first()
            valid, response = self.authorize(user_id, job_id, job)
            if not valid:
                return response

            # TODO: stop computation, delete computed results, stop creating costs > delete everything related to job!
            if job.status == JobStatus.queued:
                # TODO: remove job from queue
                pass
            elif job.status == JobStatus.running:
                # TODO: stop computation, stop creating costs
                pass
            # TODO: check if results were computed and if delete them

            self.db.delete(job)
            self.db.commit()

            return {
                "status": "success",
                "code": 204
            }

        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1jobs~1{job_id}/delete"]).to_dict()

    @rpc
    def get_all(self, user_id: str):
        """The request will ask the back-end to get all available jobs for the given user.

        Keyword Arguments:
            user_id {str} -- The identifier of the user
        """
        try:
            jobs = self.db.query(Job).filter_by(user_id=user_id).order_by(Job.created_at).all()

            return {
                "status": "success",
                "code": 200,
                "data": {
                    "jobs": JobSchema(many=True).dump(jobs).data,
                    "links": []
                }
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1jobs/get"]).to_dict()

    @rpc
    def create(self, user_id: str, **job_args):
        """The request will ask the back-end to create a new job using the description send in the request body.

        Keyword Arguments:
            user_id {str} -- The identifier of the user
            job_args {dict} -- The information needed to create a job
        """
        try:
            process_graph = job_args.pop('process_graph')
            process_response = self.process_graphs_service.create(
                user_id=user_id,
                **{"process_graph": process_graph})
            if process_response["status"] == "error":
                return process_response
            process_graph_id = process_response["service_data"]
            
            job = Job(user_id, process_graph_id, **job_args)
            job_id = str(job.id)
            self.db.add(job)
            self.db.commit()
            
            if "description" not in locals():
                description = None
                
            # Create folder for job
            job_folder = self.create_folder(user_id, job_id)
            
            # Create Apache Airflow DAG file
            WriteAirflowDag(job_id, user_id, process_graph, job_folder, user_email=None, job_description=description)

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
    def process(self, user_id: str, job_id: str):
        try:        
            job = self.db.query(Job).filter_by(id=job_id).first()
            
            valid, response = self.authorize(user_id, job_id, job)
            if not valid:
                raise Exception(response)

            response = self.airflow.unpause_dag(job_id, unpause=True)

            # Update jobs database #TODO get this information from airflow database
            job.status = "running"
            self.db.commit()

            return {
                "status": "success",
                "code": 202,
            }
        except Exception as exp:
            job.status = job.status + " error: " + exp.__str__() #+ ' ' + filter_args
            self.db.commit()
            return exp

    @rpc
    def process_sync(self, user_id: str, process_graph: dict, output: dict=None,
                     plan: str=None, budget: int=None):
        """
        Creates a processes a job directly using two other functions of this class.
        """

        response = self.create(user_id=user_id, process_graph=process_graph, output=output, plan=plan, budget=budget)
        job_id = response['headers']['Location'].split('jobs/')[-1]

        _ = self.process(user_id=user_id, job_id=job_id)

        return {
            "status": "success",
            "code": 201,
            "headers": {"Location": "jobs/" + job_id }
        }


    @rpc
    def estimate(self, user_id: str, job_id: str):
        """
        Basic function to return default information about processng costs on back-end.
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

    # TODO: If build should be automated using an endpoint e.g. /build the following can be
    # activated and adapted
    # @rpc
    # def build(self, user_id: str):
    #     try:
    #         status, log, obj_image_stream = self.template_controller.build(
    #             self.api_connector,
    #             environ["CONTAINER_NAME"],
    #             environ["CONTAINER_TAG"],
    #             environ["CONTAINER_GIT_URI"],
    #             environ["CONTAINER_GIT_REF"],
    #             environ["CONTAINER_GIT_DIR"])
    #     except Exception as exp:
    #         return ServiceException(500, user_id, str(exp),
    #             links=["#tag/Job-Management/paths/~1jobs~1{job_id}~1results/delete"]).to_dict()

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
            raise Exception("Not implemented yet!")
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
            return False, ServiceException(400, user_id, "The job with id '{0}' does not exist.".format(job_id),
                                           internal=False, links=["#tag/Job-Management/paths/~1data/get"]).to_dict()

        # TODO: Permission (e.g admin)
        if job.user_id != user_id:
            return False, ServiceException(401, user_id, "You are not allowed to access this ressource.",
                                           internal=False, links=["#tag/Job-Management/paths/~1data/get"]).to_dict()

        return True, None
        
    def create_folder(self, user_id:str, job_id:str):
        """
        
        """
        
        # NB this method to be deleted whenn this functionality provided by file management microservice
        # Path to folder where temp/final job data is stored (no trailing slash)
        foldername = os.environ["JOB_DATA"] + os.path.sep + user_id + os.path.sep + job_id
        if not os.path.isdir(foldername):
            os.makedirs(foldername)
        
        return foldername

    # @rpc
    # def get_job(self, user_id, job_id):
    #     try:
    #         job = self.db.query(Job).filter_by(id=job_id).first()

    #         if not job:
    #             raise BadRequest("Job with id '{0}' does not exist.").format(job_id)

    #         if job.user_id != user_id:
    #             raise Forbidden("You don't have the permission to access job with id '{0}'.").format(job_id)

    #         return {
    #             "status": "success",
    #             "data": JobSchemaFull().dump(job).data
    #         }
    #     except BadRequest:
    #         return {"status": "error", "service": self.name, "key": "BadRequest", "msg": str(exp)}
    #     except Forbidden:
    #         return {"status": "error", "service": self.name, "key": "Forbidden", "msg": str(exp)}
    #     except Exception as exp:
    #         return {"status": "error", "service": self.name, "key": "InternalServerError", "msg": str(exp)}

    # @rpc
    # def process_job(self, job_id):
    #     try:
    #         job = self.db.query(Job).filter_by(id=job_id).first()
    #         tasks = self.db.query(Task).filter_by(job_id=job_id).all()
    #         processes = self.process_service.get_all_processes_full()["data"]

    #         tasks = sorted(tasks, key=lambda task: task.seq_num)

    #         job.status = "running"
    #         self.db.commit()

    #         data_filter = tasks[0]

    #         pvc = self.data_service.prepare_pvc(data_filter)["data"]

    #         # TODO: Implement in Extraction Service
    #         filter = tasks[0]
    #         product = filter.args["product"]
    #         start = filter.args["filter_daterange"]["from"]
    #         end = filter.args["filter_daterange"]["to"]
    #         left = filter.args["filter_bbox"]["left"]
    #         right = filter.args["filter_bbox"]["right"]
    #         top = filter.args["filter_bbox"]["top"]
    #         bottom = filter.args["filter_bbox"]["bottom"]
    #         srs = filter.args["filter_bbox"]["srs"]

    #         bbox = [top, left, bottom, right]

    #         # in_proj = Proj(init=srs)
    #         # out_proj = Proj(init='epsg:4326')
    #         # in_x1, in_y1 = bottom, left
    #         # in_x2, in_y2 = top, right
    #         # out_x1, out_y1 = transform(in_proj, out_proj, in_x1, in_y1)
    #         # out_x2, out_y2 = transform(in_proj, out_proj, in_x2, in_y2)
    #         # bbox = [out_x1, out_y1, out_x2, out_y2]

    #         file_paths = self.data_service.get_records(qtype="file_paths", qname=product, qgeom=bbox, qstartdate=start, qenddate=end)["data"]
    #         tasks[0].args["file_paths"] = file_paths

    #         pvc = self.template_controller.create_pvc(self.api_connector, "pvc-" + str(job.id), "storage-write", "5Gi")     # TODO: Calculate storage size and get storage class
    #         previous_folder = None
    #         for idx, task in enumerate(tasks):
    #             try:
    #                 template_id = "{0}-{1}".format(job.id, task.id)

    #                 for p in processes:
    #                     if p["process_id"] == task.process_id:
    #                         process = p

    #                 config_map = self.template_controller.create_config(
    #                     self.api_connector,
    #                     template_id,
    #                     {
    #                         "template_id": template_id,
    #                         "last": previous_folder,
    #                         "args": task.args
    #                     })

    #                 image_name = process["process_id"].replace("_", "-").lower() # TODO: image name in process spec

    #                 status, log, obj_image_stream = self.template_controller.build(
    #                     self.api_connector,
    #                     template_id,
    #                     image_name,
    #                     "latest",   # TODO: Implement tagging in process service
    #                     process["git_uri"],
    #                     process["git_ref"],
    #                     process["git_dir"])

    #                 status, log, metrics =  self.template_controller.deploy(
    #                     self.api_connector,
    #                     template_id,
    #                     obj_image_stream,
    #                     config_map,
    #                     pvc,
    #                     "500m",     # TODO: Implement Ressource Management
    #                     "1",
    #                     "256Mi",
    #                     "1Gi")

    #                 previous_folder = template_id
    #             except APIConnectionError as exp:
    #                 task.status = exp.__str__()
    #                 self.db.commit()
    #         pvc.delete(self.api_connector)
    #         job.status = "finished"
    #         self.db.commit()
    #     except Exception as exp:
    #         job.status = str(exp)
    #         self.db.commit()
