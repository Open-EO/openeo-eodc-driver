from nameko.extensions import DependencyProvider

from .templates import *
from ..exceptions import APIConnectionError


class TemplateControllerWrapper:
    def create_pvc(self, api_connector, job_id, storage_class, storage_size):
        return PersistentVolumeClaim(job_id, storage_class, storage_size).create(api_connector)
    
    def create_config(self, api_connector, template_id, args):
        return ConfigMap(template_id, args).create(api_connector)

    def build(self, api_connector, template_id, image_name, tag, git_uri, git_ref, git_dir):
        log = ""

        obj_image_stream = ImageStream(template_id, image_name, tag)
        obj_build = Build(template_id, git_uri, git_ref, git_dir, obj_image_stream)
        
        if obj_image_stream.exists(api_connector) :
            log += "Found existing image...\n"
            return "Finished Building", log, obj_image_stream

        log += "Building...\n"
        obj_image_stream.create(api_connector, watch=False)
        obj_build.create(api_connector)

        log += obj_build.get_logs(api_connector)

        # obj_build.delete(api_connector) # TODO: Debug -> If pod does not exist anymore (build) -> vllt wegen falscher refernzierung bei delete()?

        return "Finished Building", log, obj_image_stream

    def deploy(self, api_connector, template_id, obj_image_stream, obj_config_map, obj_pvc, cpu_request, cpu_limit, mem_request, mem_limit):
        log = ""

        obj_job = Job(template_id, obj_image_stream, obj_config_map, obj_pvc, cpu_request, cpu_limit, mem_request, mem_limit)
        
        log += "Deploying..."
        obj_job.create(api_connector)

        log += obj_job.get_logs(api_connector)
        # metrics = obj_job.get_metrics(api_connector) # TODO: Metrics Error Bug Fixing -> Process to fast executed for metrics

        # obj_job.delete(api_connector) # TODO: Deactivated just for showcasing
        
        return "Finished Deploying", log, []

    # def __set_status(self, status, log="", metrics={}, error=False):
    #     self.status = status
    #     self.__log = self.__log + " -> {0}\n{1}".format(status, log)
    #     self.__metrics = self.__metrics
    #     if error:
    #         self.__error = True

class TemplateController(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return TemplateControllerWrapper()