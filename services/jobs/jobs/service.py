from os import environ
from nameko.rpc import rpc, RpcProxy
from nameko_sqlalchemy import DatabaseSession

from .models import Base, Job, Task
from .schema import JobSchema, JobSchemaFull
from .exceptions import BadRequest, Forbidden, APIConnectionError
from .dependencies.taskparser import TaskParser
from .dependencies.validator import Validator
from .dependencies.api_connector import APIConnector
from .dependencies.template_controller import TemplateController

class JobService:
    name = "jobs"

    db = DatabaseSession(Base)
    process_service = RpcProxy("processes")
    data_service = RpcProxy("data")
    validator = Validator()
    taskparser = TaskParser()
    api_connector = APIConnector()
    template_controller = TemplateController()

    @rpc
    def create_job(self, user_id, process_graph, output):
        try:
            processes = self.process_service.get_all_processes_full()["data"]
            products = self.data_service.get_records()["data"]
            
            self.validator.update_datasets(processes, products)
            self.validator.validate_node(process_graph)

            job = Job(user_id, process_graph, output)
            self.db.add(job)
            self.db.commit()

            tasks = self.taskparser.parse_process_graph(job.id, process_graph)
            for idx, task in enumerate(tasks):
                self.db.add(task)
                self.db.commit()

            return {
                "status": "success",
                "data": JobSchema().dump(job)
            }
        except BadRequest:
            return {"status": "error", "exc_key":  "BadRequest"}
        except Exception as exp:
            return {"status": "error", "exc_key":  "InternalServerError"}
    
    @rpc
    def get_job(self, user_id, job_id):
        try:
            job = self.db.query(Job).filter_by(id=job_id).first()

            if not job:
                raise BadRequest

            if job.user_id != user_id:
                raise Forbidden

            return {
                "status": "success",
                "data": JobSchemaFull().dump(job)
            }
        except BadRequest:
            return {"status": "error", "exc_key":  "BadRequest"}
        except Forbidden:
            return {"status": "error", "exc_key":  "Forbidden"}
        except Exception as exp:
            return {"status": "error", "exc_key":  "InternalServerError"}
    
    @rpc
    def process_job(self, job_id):
        try:
            job = self.db.query(Job).filter_by(id=job_id).first()
            tasks = self.db.query(Task).filter_by(job_id=job_id).all()

            pvc = self.api_connector.create_pvc(self.api_connector, job.id, "5Gi", "storage_write")     # TODO: Calculate storage size and get storage class
            previous_folder = None
            for idx, task in enumerate(tasks):
                # if idx == 0:


                try:
                    template_id = "{0}-{1}".format(job.id, task.id)
                    process = self.process_service.get_process(task.process_id)["data"]
                    
                    config_map = self.api_connector.create_config(
                        self.api_connector, 
                        template_id, 
                        {
                            "template_id": template_id,
                            "last": previous_folder,
                            "args": task.args
                        })

                    status, log, obj_image_stream = self.template_controller.build(
                        self.api_connector, 
                        template_id, 
                        process.process_id,
                        "latest",   # TODO: Implement tagging in process service
                        process.git_uri, 
                        process.git_ref, 
                        process.git_dir)

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
        except Exception as exp:
            job.status = str(exp)
            self.db.commit()
