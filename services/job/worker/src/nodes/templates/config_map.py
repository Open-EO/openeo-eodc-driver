''' Template for OpenShift ConfigMap '''

from json import dumps
from .base_template import BaseTemplate

class ConfigMap(BaseTemplate):
    ''' Class for OpenShift ConfigMap Object '''

    def __init__(self, namespace, process_selector, data, input_pvcs):
        
        template_id = process_selector + "-cfg"
        path = "/api/v1/namespaces/{0}/configmaps"

        input_mounts = []
        for input_pvc in input_pvcs:
            input_mounts.append("/" + input_pvc.template_id)

        super().__init__(namespace, template_id, path, "ConfigMap", "v1")

        self.template["data"] = {
            "config.json": dumps(data),
            "input_mounts.json": dumps(input_mounts)
        }

    def check_status(self, response, auth=None):
        if "data" in response:
            return True
        return False