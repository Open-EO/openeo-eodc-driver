''' Template for OpenShift BuildConfig '''

from service.src.templates.base_template import BaseTemplate

class BuildConfig(BaseTemplate):
    ''' Class for OpenShift BuildConfig Object '''

    def __init__(self, payload):
        path = "/oapi/v1/namespaces/{0}/buildconfigs"
        validation = {
            "git_uri": r"(git@([a-z]|.|-|_|/)+.git$|https://([a-z]|.|-|_|/)+.git$)",
            "git_ref": r"[a-z]+",
            "image_name": r"([a-z]|-){5,}",
            "tag": r"[a-z]+",
        }

        super().__init__("BuildConfig", "v1", path, validation, payload)

        self.template["spec"] = {
            "source": {
                "type": "Git",
                "git": {
                    "uri": self.vars["git_uri"],
                    "ref": self.vars["git_ref"]
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
                    "name": "{0}:{1}".format(self.vars["image_name"], self.vars["tag"])
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
