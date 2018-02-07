''' Template for OpenShift ConfigMap '''

from json import dumps
from service.src.templates.base_template import BaseTemplate

class ConfigMap(BaseTemplate):
    ''' Class for OpenShift ConfigMap Object '''

    def __init__(self, payload):
        path = "/api/v1/namespaces/{0}/configmaps"
        validation = {
            "data": None
        }

        super().__init__("ConfigMap", "v1", path, validation, payload)

        self.template["data"] = {
            "parameters.json": dumps(self.vars["data"])
        }
