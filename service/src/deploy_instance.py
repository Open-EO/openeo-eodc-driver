''' Deployment Class of the EODC Template Engine  '''

from service.src.exceptions import TemplateException, DeployException
from service.src.templates.persistant_volume_claim import PersistentVolumeClaim
from service.src.templates.config_map import ConfigMap
from service.src.templates.job import Job

class DeployInstance:
    ''' DeployInstance class has the templates of the deployment and handles execution. '''

    def __init__(self, payload):
        if "pvc" not in payload:
            raise DeployException("Missing PersitantVolumeClaim Configurations.")
        if "config_map" not in payload:
            raise DeployException("Missing ConfigMap Configurations.")
        if "job" not in payload:
            raise DeployException("Missing Job Configurations.")

        try:
            self.pvc = PersistentVolumeClaim(payload["pvc"])
            self.config_map = ConfigMap(payload["config_map"])
            self.job = Job(payload["job"])
        except TemplateException as exp:
            raise DeployException("Exeption in Deploy instantiation: " + str(exp))

    def perform_deploy(self):
        ''' Performs Deployment of the job '''

        try:
            self.pvc.execute()
            self.config_map.execute()
            name, self_link = self.job.execute()
        except TemplateException as exp:
            raise DeployException("Exception in Deploy execution: " + str(exp))

        return name, self_link