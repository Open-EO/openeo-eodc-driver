''' Template for OpenShift ConfigMap '''

from json import dumps
from .base import BaseTemplate

class ConfigMap(BaseTemplate):
    ''' Class for OpenShift ConfigMap Object '''

    def __init__(self, template_id, data):
        path = "/api/v1/namespaces/{0}/configmaps"
        super().__init__(template_id, path, "ConfigMap", "v1")

        self.selfLinks["template"] = "{0}/{1}".format(path, template_id)
        self.data = data

        self.template["data"] = {
            "config.json": dumps(data)
        }

    def is_ready(self, api_connector):
        for response in api_connector.watch("openshift", self.selfLinks["template"]):
            if "data" in response:
                return
    
    def extract_selfLinks(self, response, api_connector):
        pass
