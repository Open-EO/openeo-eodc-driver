from os import environ
from nameko.rpc import rpc, RpcProxy
from nameko_sqlalchemy import DatabaseSession

from .models import Base, Job, Task
from .schema import JobSchema, JobSchemaFull
from .exceptions import BadRequest, Forbidden, APIConnectionError
from .dependencies.task_parser import TaskParser
from .dependencies.validator import Validator
from .dependencies.api_connector import APIConnector
from .dependencies.template_controller import TemplateController
from .dependencies.operations import Operations

class JobService:
    name = "jobs"

    db = DatabaseSession(Base)
    process_service = RpcProxy("processes")
    data_service = RpcProxy("data")
    validator = Validator()
    taskparser = TaskParser()
    api_connector = APIConnector()
    template_controller = TemplateController()
    operations = Operations()

    @rpc
    def health(self, request):
        return { "status": "success"}

    @rpc
    def create_job(self, user_id, process_graph, output):
        try:
            processes = self.get_processes()
            products = self.get_products()
            
            self.validator.update_datasets(processes, products)
            self.validator.validate_node(process_graph)

            job = Job(user_id, process_graph, output)
            self.db.add(job)
            self.db.commit()

            tasks = self.taskparser.parse_process_graph(job.id, process_graph, processes, products)
            tasks[0].args["file_paths"] = self.get_file_paths(tasks[0])

            for task in tasks:
                self.db.add(task)
                self.db.commit()

            return {
                "status": "success",
                "data": JobSchema().dump(job).data
            }
        except BadRequest as exp:
            return {"status": "error", "service": self.name, "key": "BadRequest", "msg": str(exp)}
        except Exception as exp:
            return {"status": "error", "service": self.name, "key": "InternalServerError", "msg": str(exp)}
    
    @rpc
    def get_job(self, user_id, job_id):
        try:
            job = self.db.query(Job).filter_by(id=job_id).first()

            if not job:
                raise BadRequest("Job with id '{0}' does not exist.".format(job_id))

            if job.user_id != user_id:
                raise Forbidden("You don't have the permission to access job with id '{0}'.".format(job_id))

            return {
                "status": "success",
                "data": JobSchemaFull().dump(job).data
            }
        except BadRequest:
            return {"status": "error", "service": self.name, "key": "BadRequest", "msg": str(exp)}
        except Forbidden:
            return {"status": "error", "service": self.name, "key": "Forbidden", "msg": str(exp)}
        except Exception as exp:
            return {"status": "error", "service": self.name, "key": "InternalServerError", "msg": str(exp)}
    
    @rpc
    def process_job(self, job_id):
        try:
            job, tasks = self.get_job_tasks(job_id)
            processes = self.get_processes()

            job.status = "running"
            self.db.commit()

            vrt = [] # TODO
            for task in tasks:
                #TODO: Check if user-defined function
                vrt = self.operations.map(task.process_id, task.args, vrt)

            pvc = self.template_controller.create_pvc(api_connector, "pvc-" + str(job.id), "storage-write", "5Gi")

            # TODO: Calculate estimated storage size
            # TODO: Define storage class
            # TODO: Specify storage req. for process
            storage_class = "storage-write"
            storage_size = "5Gi"
            cpu_request = "500m"
            cpu_limit = "1"
            mem_request = "256Mi"
            mem_limit = "1Gi"

            image_name = "base-image" # TODO Naming
            pvc = self.template_controller.create_pvc(self.api_connector, "pvc-" + str(job.id), "storage-write", "5Gi")
            config_map = self.template_controller.create_config(self.api_connector, job.id, vrt)
            job = self.template_controller.create_job(
                self.api_connector, 
                vrt, 
                job, 
                storage_class, 
                storage_size, 
                cpu_request, 
                cpu_limit, 
                mem_request, 
                mem_limit
            )



            

            job = self.template_controller.create_job(self.api_connector, job.id, vrt)

            deploy(self, api_connector, vrt, job, "storage-write", "5Gi", "500m", "1", "256Mi", "1Gi"):

            status, log, metrics =  self.template_controller.deploy(
                self.api_connector, 
                template_id,
                obj_image_stream, 
                config_map,
                pvc,
                "500m",     # TODO: Implement Ressource Management
                "1", 
                "256Mi", 
                "1Gi")
            

            status, log, obj_image_stream = self.template_controller.build(
                self.api_connector, 
                template_id, 
                image_name,
                "latest",   # TODO: Implement tagging in process service
                process["git_uri"], 
                process["git_ref"], 
                process["git_dir"])

                
            try:
                template_id = "{0}-{1}".format(job.id, task.id)

                for process in processes:
                    if process["process_id"] == task.process_id:
                        break
                
                config_map = self.template_controller.create_config(
                    self.api_connector, 
                    template_id, 
                    {
                        "template_id": template_id,
                        "last": previous_folder,
                        "args": task.args
                    })
                
                image_name = process["process_id"].replace("_", "-").lower() # TODO: image name in process spec

                status, log, obj_image_stream = self.template_controller.build(
                    self.api_connector, 
                    template_id, 
                    image_name,
                    "latest",   # TODO: Implement tagging in process service
                    process["git_uri"], 
                    process["git_ref"], 
                    process["git_dir"])

                status, log, metrics =  self.template_controller.deploy(
                    self.api_connector, 
                    template_id,
                    obj_image_stream, 
                    config_map,
                    pvc,
                    "500m",     # TODO: Implement Ressource Management
                    "1", 
                    "256Mi", 
                    "1Gi")
                
                previous_folder = template_id
            except APIConnectionError as exp:
                task.status = exp.__str__()
                self.db.commit()
                break

            pvc.delete(self.api_connector)
            job.status = "finished"
            self.db.commit()
        except Exception as exp:
            job.status = str(exp) # TODO: error message field for jobs?
            self.db.commit()


    def get_job_tasks(self, job_id):
        job = self.db.query(Job).filter_by(id=job_id).first()
            
        if not job:
            raise BadRequest("Job with id '{0}' does not exist.".format(job_id))

        tasks = self.db.query(Task).filter_by(job_id=job_id).all()

        if not tasks:
            raise BadRequest("Job with id '{0}' has no tasks.".format(job_id))

        tasks = sorted(tasks, key=lambda task: task.seq_num)

        return job, tasks
    
    def get_processes(self):
        rpc_response = self.process_service.get_all_processes_full()
        if rpc_response["status"] == "error":
            raise BadRequest(rpc_response["msg"])

        return rpc_response["data"]
    
    def get_products(self):
        rpc_response = self.data_service.get_records()
        if rpc_response["status"] == "error":
            raise BadRequest(rpc_response["msg"])

        return rpc_response["data"]
    
    def get_file_paths(self, task):
        # TODO: Implement in Extraction Service
            rpc_response = self.data_service.get_records(
                qtype="file_paths", 
                qname=task.args["product"], 
                qgeom={
                    "left": task.args["filter_bbox"]["left"],
                    "right": task.args["filter_bbox"]["right"],
                    "top": task.args["filter_bbox"]["top"],
                    "bottom": task.args["filter_bbox"]["bottom"],
                    "srs": task.args["filter_bbox"]["srs"]
                },
                qstartdate=task.args["filter_daterange"]["from"], 
                qenddate=task.args["filter_daterange"]["to"])

            if rpc_response["status"] == "error":
                raise BadRequest(rpc_response["msg"])

            return rpc_response["data"]   
       
