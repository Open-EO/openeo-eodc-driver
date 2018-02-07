''' Template for OpenShift PersistentVolumeClaim '''

from service.src.templates.base_template import BaseTemplate

class PersistentVolumeClaim(BaseTemplate):
    ''' Class for OpenShift PersistentVolumeClaim Object '''

    def __init__(self, payload):

        path = "/api/v1/namespaces/{0}/persistentvolumeclaims"
        validation = {
            "class_name": r"([a-z]|-)+",
            "modes": r"^(ReadWriteOnce|ReadOnlyMany|ReadWriteMany){1}$",
            "size": r"^\d+(Gi|Mi){1}$"
        }

        super().__init__("PersistentVolumeClaim", "v1",  path, validation, payload)

        self.template["spec"] = {
            "storageClassName": self.vars["class_name"],
            "accessModes": [self.vars["modes"]],
            "resources": {
                "requests": {
                    "storage": self.vars["size"]
                }
            }
        }
