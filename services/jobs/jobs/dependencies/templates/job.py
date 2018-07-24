''' Template for OpenShift Job '''

from urllib.parse import quote
from .base import BaseTemplate, APIConnectionError


class Job(BaseTemplate):
    ''' Class for OpenShift Job Object '''

    __METRICS = [
        "cpu/usage_rate",
        "memory/usage",
        "network/rx_rate",
        "network/tx_rate"
    ]

    def __init__(self, template_id, imagestream, configmap, out_pvc, cpu_request, cpu_limit, mem_request, mem_limit):
        path = "/apis/batch/v1/namespaces/{0}/jobs"
        super().__init__(template_id, path, "Job", "batch/v1")

        volumes = [
            {
                "name": "eodc-volume",
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
                "name": "data-volume",
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
                "name": "eodc-volume",
                "mountPath": "/eodc/products"
            },
            {
                "name": "config-volume",
                "mountPath": "/job_config"
            },
            {
                "name": "data-volume",
                "mountPath": "/job_data"
            },
            {
                "name": "results-volume",
                "mountPath": "/job_results"
            }
        ]

        self.template["spec"] = {
            "template": {
                "spec": {
                    "restartPolicy": "OnFailure",
                    "containers": [{
                        "name": self.template_id,
                        "image": imagestream.selfLinks["dockerImageRepository"] + ":latest",
                        "volumeMounts": volumeMounts,
                        "resources": {
                            "limits": {
                                "memory": mem_limit,
                                "cpu": cpu_limit
                            },
                            "requests": {
                                "memory": mem_request,
                                "cpu": cpu_request
                            }
                        }
                    }],
                    "securityContext": {
                        "supplementalGroups": [60028, 65534]
                    },
                    "volumes": volumes
                }
            }
        }

    def is_ready(self, api_connector):
        for response in api_connector.watch("openshift", self.selfLinks["job"]):
            if "status" in response:
                if "succeeded" in response["status"]:
                    return
                if "failed" in response["status"]:
                    raise APIConnectionError(409, response)

    def extract_selfLinks(self, response, api_connector):
        self.selfLinks["job"] = response["metadata"]["selfLink"]

        pods = api_connector.request(
            "openshift", "get", "/api/v1/namespaces/{0}/pods")
        for pod in pods["items"]:
            if pod["metadata"]["name"].startswith(self.template_id):
                self.selfLinks["pod"] = pod["metadata"]["selfLink"]

    def get_logs(self, api_connector):
        return api_connector.request("openshift", "get", self.selfLinks["pod"] + "/log")

    def get_metrics(self, api_connector):
        pod = api_connector.request("openshift", "get", self.selfLinks["pod"])

        data = {}
        if "containerStatuses" in pod["status"]:
            pod_name = pod["metadata"]["name"]
            metrics = api_connector.request(
                "hawkular", "get", "/metrics?tags=pod_name:" + pod_name)

            for metric in metrics:
                m_name = metric["tags"]["descriptor_name"]
                if m_name in self.__METRICS:
                    m_path = "/{0}s/{1}/data".format(
                        metric["type"], quote(metric["id"], safe=''))
                    m_data = api_connector.request("hawkular", "get", m_path)
                    data[m_name] = m_data[::-1]
        return data
