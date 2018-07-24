''' Template for OpenShift BuildConfig '''

from .base import BaseTemplate, TemplateError

class Build(BaseTemplate):
    ''' Class for OpenShift Build Object '''

    def __init__(self, template_id, git_uri, git_ref, git_dir, img_stream):
        path = "/oapi/v1/namespaces/{0}/builds"
        super().__init__(template_id, path, "Build", "v1")

        self.git_uri = git_uri
        self.git_ref = git_ref
        self.git_dir = git_dir
        self.img_stream = img_stream

        self.template["spec"] = {
            "source": {
                "type": "Git",
                "git": {
                    "uri": git_uri,
                    "ref": git_ref
                },
                "sourceSecret": {
                    "name": "eodc-builder"
                }
            },
            "strategy": {
                "dockerStrategy": {
                    "dockerfilePath": "Dockerfile"
                }
            },
            "output": {
                "to": {
                    "kind": "ImageStreamTag",
                    "name": "{0}:{1}".format(img_stream.image_name, img_stream.tag)
                }
            }
        }

        if git_dir:
            self.template["spec"]["source"]["contextDir"] = git_dir

    def is_ready(self, api_connector):
        for response in api_connector.watch("openshift", self.selfLinks["build"]):
            status = response["status"]["phase"]
            if status == "Complete" or status == "Failed":
                return

    def extract_selfLinks(self, response, api_connector):
        self.selfLinks["build"] = response["metadata"]["selfLink"]
        
        pod_request = api_connector.request("openshift", "get", self.selfLinks["build"])
        if "annotations" in pod_request["metadata"]:
            pods_path = "/api/v1/namespaces/{0}/pods/"
            self.selfLinks["pod"] = pods_path + pod_request["metadata"]["annotations"]["openshift.io/build.pod-name"]
    
    def get_logs(self, api_connector):
        return api_connector.request("openshift", "get", self.selfLinks["pod"] + "/log")
