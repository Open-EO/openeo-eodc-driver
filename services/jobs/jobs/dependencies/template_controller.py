from nameko.extensions import DependencyProvider

from .templates import *
from ..exceptions import APIConnectionError


class TemplateControllerWrapper:
    def create_pvc(self, api_connector, job_id, storage_class, storage_size):
        return PersistentVolumeClaim(job_id, storage_class, storage_size).create(api_connector)
    
    def create_config(self, api_connector, template_id, args):
        return ConfigMap(template_id, args).create(api_connector)
    
    def create_job(self, api_connector, template_id, img_, obj_config_map, obj_pvc):
        return Job(template_id, obj_image_stream, obj_config_map, obj_pvc, cpu_request, cpu_limit, mem_request, mem_limit).create(api_connector)

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

    def deploy(self, api_connector, vrt, job, storage_class, storage_size, cpu_request, cpu_limit, mem_request, mem_limit):
        
        config_map = self.create_config(api_connector, job.id, vrt)
        job = self.create_job(api_connector, job.id, pvc, config_map, "500m", "1", "256Mi", "1Gi")

        log = job.get_logs(api_connector)
        metrics = job.get_metrics(api_connector) # TODO: Metrics Error Bug Fixing -> Process to fast executed for metrics?

        job.delete(api_connector)

        return log, metrics


class TemplateController(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return TemplateControllerWrapper()