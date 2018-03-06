''' Template for OpenShift BuildConfig '''

from os import environ
from json import loads
from requests import get, delete
from .base_template import BaseTemplate

class BuildConfig(BaseTemplate):
    ''' Class for OpenShift BuildConfig Object '''

    def __init__(self, namespace, build_name, git_uri, git_ref, git_dir, img_stream):

        template_id = build_name
        path = "/oapi/v1/namespaces/{0}/buildconfigs"

        super().__init__(namespace, template_id, path, "BuildConfig", "v1")

        self.template["spec"] = {
            "source": {
                "type": "Git",
                "git": {
                    "uri": git_uri,
                    "ref": git_ref
                }
                # TODO: If fetched with secret -> Must be specified
                # "sourceSecret": {
                #     "name": "eodc-builder"
                # }
            },
            "strategy": {
                "dockerStrategy": {
                    "dockerfilePath": "Dockerfile"
                }
            },
            "output": {
                "to": {
                    "kind": "ImageStreamTag",
                    "name": img_stream.template_id + ":latest"
                }
            },
            "triggers": [
                {
                    "type": "ConfigChange"
                },
                {
                    "type": "ImageChange",
                    "imageChange": None
                }
            ]
        }

        if git_dir:
            self.template["spec"]["source"]["contextDir"] = git_dir

    def check_status(self, response, auth=None):
        version = response["status"]["lastVersion"]
        verify = True if environ.get("VERIFY") == "true" else False

        pod_url = "{0}/api/v1/namespaces/{1}/pods/{2}-{3}-build".format(environ.get("OPENSHIFT_API"), self.namespace, self.template_id, version)
        pod_response = get(pod_url, headers=auth, verify=verify)

        if pod_response.ok == False:
            self.raise_error(pod_response.text)
        
        pod_json = loads(pod_response.text)

        if pod_json["status"]["phase"] == "Pending":
            self.status = "Pending"
            return False
        
        if pod_json["status"]["phase"] == "Running":
            self.status = "Running"
            return False
        
        if pod_json["status"]["phase"] == "Succeeded":
            self.status = "Finished"
            return True

        return False
