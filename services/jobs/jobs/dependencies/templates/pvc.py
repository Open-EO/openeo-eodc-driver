''' Template for OpenShift Persitant Volume Claim '''

from .base import BaseTemplate

class PersistentVolumeClaim(BaseTemplate):
    ''' Class for OpenShift PersistentVolumeClaim Object '''

    def __init__(self, template_id, storage_class, storage_size):
        path = "/api/v1/namespaces/{0}/persistentvolumeclaims"
        super().__init__(template_id, path, "PersistentVolumeClaim", "v1")

        self.selfLinks["template"] = "{0}/{1}".format(path, template_id)
        self.storage_class = storage_class
        self.storage_size = storage_size

        self.template["spec"] = {
            "storageClassName": storage_class,
            "accessModes": ["ReadWriteOnce"],
            "persistentVolumeReclaimPolicy": "Recycle",
            "resources": {
                "requests": {
                    "storage": storage_size
                }
            }
        }

    def is_ready(self, api_connector):
        for response in api_connector.watch("openshift", self.selfLinks["template"]):
            if "status" in response and "phase" in response["status"] and "Bound" in response["status"]["phase"]:
                return
    
    def extract_selfLinks(self, response, api_connector):
        pass
