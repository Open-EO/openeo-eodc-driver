''' Template for OpenShift ImageStream '''

from worker.templates.base_template import BaseTemplate

class ImageStream(BaseTemplate):
    ''' Class for OpenShift ImageStream Object '''

    def __init__(self, namespace, process_selector):

        template_id = process_selector + "-ims"
        path = "/oapi/v1/namespaces/{0}/imagestreams"

        super().__init__(namespace, template_id, path, "ImageStream", "v1")

        self.link = "docker-registry.default.svc:5000/{0}/{1}".format(namespace, template_id)

        self.template["spec"] = {
            "tags": [
                {
                    "name": "latest"
                }
            ]
        }
    
    def check_status(self, response, auth=None):
        if "dockerImageRepository" in response["status"]:
            self.link = response["status"]["dockerImageRepository"]
            return True
        
        return False