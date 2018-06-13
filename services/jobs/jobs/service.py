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
    def health(self, request):
        return { "status": "success"}

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

            tasks = self.taskparser.parse_process_graph(job.id, process_graph, processes)
            for idx, task in enumerate(tasks):
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
                raise BadRequest("Job with id '{0}' does not exist.").format(job_id)

            if job.user_id != user_id:
                raise Forbidden("You don't have the permission to access job with id '{0}'.").format(job_id)

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
            job = self.db.query(Job).filter_by(id=job_id).first()
            tasks = self.db.query(Task).filter_by(job_id=job_id).all()
            processes = self.process_service.get_all_processes_full()["data"]

            tasks = sorted(tasks, key=lambda task: task.seq_num)

            job.status = "running"
            self.db.commit()

            data_filter = tasks[0]

            pvc = self.data_service.prepare_pvc(data_filter)["data"]

            # TODO: Implement in Extraction Service
            filter = tasks[0]
            product = filter.args["product"]
            start = filter.args["filter_daterange"]["from"]
            end = filter.args["filter_daterange"]["to"]
            left = filter.args["filter_bbox"]["left"]
            right = filter.args["filter_bbox"]["right"]
            top = filter.args["filter_bbox"]["top"]
            bottom = filter.args["filter_bbox"]["bottom"]
            srs = filter.args["filter_bbox"]["srs"]

            bbox = [top, left, bottom, right]

            # in_proj = Proj(init=srs)
            # out_proj = Proj(init='epsg:4326')
            # in_x1, in_y1 = bottom, left
            # in_x2, in_y2 = top, right
            # out_x1, out_y1 = transform(in_proj, out_proj, in_x1, in_y1)
            # out_x2, out_y2 = transform(in_proj, out_proj, in_x2, in_y2)
            # bbox = [out_x1, out_y1, out_x2, out_y2]

            file_paths = self.data_service.get_records(qtype="file_paths", qname=product, qgeom=bbox, qstartdate=start, qenddate=end)["data"]
            tasks[0].args["file_paths"] = file_paths

            pvc = self.template_controller.create_pvc(self.api_connector, "pvc-" + str(job.id), "storage-write", "5Gi")     # TODO: Calculate storage size and get storage class
            previous_folder = None
            for idx, task in enumerate(tasks):
                try:
                    template_id = "{0}-{1}".format(job.id, task.id)

                    for p in processes:
                        if p["process_id"] == task.process_id:
                            process = p
                    
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
            pvc.delete(self.api_connector)
            job.status = "finished"
            self.db.commit()
        except Exception as exp:
            job.status = str(exp)
            self.db.commit()
