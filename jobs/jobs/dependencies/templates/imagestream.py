''' Template for OpenShift ImageStream '''

from .base import BaseTemplate

class ImageStream(BaseTemplate):
    ''' Class for OpenShift ImageStream Object '''

    def __init__(self, template_id, image_name, tag):
        path = "/oapi/v1/namespaces/{0}/imagestreams"
        super().__init__(image_name, path, "ImageStream", "v1")

        self.selfLinks["template"] = "{0}/{1}".format(path, image_name)
        self.image_name = image_name
        self.tag = tag

        self.template["spec"] = {
            "tags": [
                {
                    "name": tag
                }
            ]
        }

    def is_ready(self, api_connector):
        for response in api_connector.watch("openshift", self.selfLinks["template"]):
            if "tags" in response["status"] and self.tag in response["status"]["tags"]:
                return
    
    def extract_selfLinks(self, response, api_connector):
        self.selfLinks["dockerImageRepository"] = response["status"]["dockerImageRepository"]
