''' Template for OpenShift Job '''

from os import environ
from .base_template import BaseTemplate

class Job(BaseTemplate):
    ''' Class for OpenShift Job Object '''

    def __init__(self, namespace, process_selector, imagestream, in_pvcs, out_pvc, configmap):

        template_id = process_selector + "-job"
        path = "/apis/batch/v1/namespaces/{0}/jobs"

        super().__init__(namespace, template_id, path, "Job", "batch/v1")

        volumes = [
            {
                "name": "vol-eodc",
                "persistentVolumeClaim": {
                    "claimName": "pvc-eodc"
                }
            },
            {
                "name": "config-volume",
                "configMap": {
                    "name": configmap.template_id
                }
            },
            {
                "name": "out-volume",
                "persistentVolumeClaim": {
                    "claimName": out_pvc.template_id
                }
            },
            {
                "name": "results-volume",
                "persistentVolumeClaim": {
                    "claimName": "pvc-results"
                }
            }
        ]

        volumeMounts = [
            {
                "name": "vol-eodc",
                "mountPath": "/eodc/products"
            },
            {
                "name": "config-volume",
                "mountPath": "/job_config"
            },
            {
                "name": "out-volume",
                "mountPath": "/job_out"
            },
            {
                "name": "results-volume",
                "mountPath": "/job_results"
            }
        ]

        for pvc in in_pvcs:
            volumes.append(
                {
                    "name": pvc.template_id,
                    "persistentVolumeClaim": {
                        "claimName": pvc.template_id
                    }
                }
            )

            volumeMounts.append(
                {
                    "name": pvc.template_id,
                    "mountPath": "/" + pvc.template_id
                }
            )

        self.template["spec"] = {
            "template": {
                "spec": {
                    "restartPolicy": "OnFailure",
                    "containers":[{
                        "name": self.template_id,
                        "image": imagestream.link + ":latest",
                        "volumeMounts": volumeMounts
                    }],
                    "securityContext": {
                        "supplementalGroups": [60028, 65534]
                    },
                    "volumes": volumes
                }
            }
        }

    def check_status(self, response, auth=None):
        if "succeeded" in response["status"]:
            self.status = "Finished"
            return True
        
        self.status = "Running"

        return False
