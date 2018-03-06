''' Template for OpenShift ImageStream '''

from os import environ
from requests import get
from .base_template import BaseTemplate

class ImageStream(BaseTemplate):
    ''' Class for OpenShift ImageStream Object '''

    def __init__(self, namespace, image_name):

        template_id = image_name
        path = "/oapi/v1/namespaces/{0}/imagestreams"

        super().__init__(namespace, template_id, path, "ImageStream", "v1")

        self.link = "docker-registry.default.svc:5000/{0}/{1}".format(namespace, template_id)

        # TODO Different Verions of images -> Not just latest (in processes db)
        self.template["spec"] = {
            "tags": [
                {
                    "name": "latest"
                }
            ]
        }
    
    def does_exist(self, token):
        ''' Checks if the image does already exist '''

        auth = {"Authorization": "Bearer " + token}
        verify = True if environ.get("VERIFY") == "true" else False
        url = "{0}{1}/{2}".format(environ.get("OPENSHIFT_API"), self.path, self.template_id)
        response = get(url, headers=auth, verify=verify)

        if response.status_code == 200:
            return True
        
        return False
    
    def check_status(self, response, auth=None):
        if "dockerImageRepository" in response["status"]:
            self.link = response["status"]["dockerImageRepository"]
            return True
        
        return False