''' Template for OpenShift Job '''

from service.src.templates.base_template import BaseTemplate

class Job(BaseTemplate):
    ''' Class for OpenShift Job Object '''

    def __init__(self, payload):

        path = "/apis/batch/v1/namespaces/{0}/jobs"
        validation = {
            "image_name": r"([a-z]|-){5,}",
            "tag": r"[a-z]+",
            "name_pvc": r"([a-z]|-){5,}",
            "name_configmap": r"([a-z]|-){5,}"
        }

        super().__init__("Job", "batch/v1", path, validation, payload)

        self.template["spec"] = {
            "template": {
                "spec": {
                    "restartPolicy": "OnFailure",
                    "containers":[{
                        "name": self.vars["name"],
                        "image": "docker-registry.default.svc:5000/{0}/{1}:{2}"\
                                    .format(self.vars["namespace"], self.vars["image_name"], self.vars["tag"]),
                        "volumeMounts": [
                            {
                                "name": "vol-eodc",
                                "mountPath": "/eodc/products"
                            },
                            {
                                "name": "vol-write",
                                "mountPath": "/write"
                            },
                            {
                                "name": "config-volume",
                                "mountPath": "/job_data"
                            }
                        ]
                    }],
                    "securityContext": {
                        "supplementalGroups": [60028, 65534]
                    },
                    "volumes": [
                        {
                            "name": "vol-eodc",
                            "persistentVolumeClaim": {
                                "claimName": "pvc-eodc"
                            }
                        },
                        {
                            "name": "vol-write",
                            "persistentVolumeClaim": {
                                "claimName": self.vars["name_pvc"]
                            }
                        },
                        {
                            "name": "config-volume",
                            "configMap": {
                                "name": self.vars["name_configmap"]
                            }
                        }
                    ]
                }
            }
        }
