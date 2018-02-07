''' Template for OpenShift ImageStream '''

from service.src.templates.base_template import BaseTemplate

class ImageStream(BaseTemplate):
    ''' Class for OpenShift ImageStream Object '''

    def __init__(self, payload):
        path = "/oapi/v1/namespaces/{0}/imagestreams"
        validation = {
            "tag": r"[a-z]+",
        }

        super().__init__("ImageStream", "v1", path, validation, payload)

        self.template["spec"] = {
            "tags": [
                {
                    "name": self.vars["tag"]
                }
            ]
        }
