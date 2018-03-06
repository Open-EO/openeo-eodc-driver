''' Template for OpenShift PersistentVolumeClaim '''

from .base_template import BaseTemplate

class PersistentVolumeClaim(BaseTemplate):
    ''' Class for OpenShift PersistentVolumeClaim Object '''

    def __init__(self, namespace, process_selector, class_name, storage):

        template_id = process_selector + "-pvc"
        path = "/api/v1/namespaces/{0}/persistentvolumeclaims"

        super().__init__(namespace, template_id, path, "PersistentVolumeClaim", "v1")
        
        self.template["spec"] = {
            "storageClassName": class_name,
            "accessModes": ["ReadWriteOnce"],
            "persistentVolumeReclaimPolicy": "Recycle",
            "resources": {
                "requests": {
                    "storage": storage
                }
            }
        }

    def check_status(self, response, auth=None):
        return (True if "Bound" in response["status"]["phase"] else False)
