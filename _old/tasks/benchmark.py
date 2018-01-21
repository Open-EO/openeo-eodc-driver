import os
import json
import requests
from celery import Celery
from service.tasks.templates.udf.t_benchmark_image import template_image
from service.tasks.templates.udf.t_benchmark_build import template_build
from service.tasks.templates.udf.t_benchmark_deployment import template_deployment

celery = Celery("benchmark-queue", broker=os.environ.get('REDIS_URL'))

class CreationError(Exception):
    ''' Error class for expections retrieved by OpenShift '''
    pass

@celery.task
def perform_benchmarking(settings):
    ''' Perform a single benchmarking job on the OpenShift environment '''

    # template["parameters"][1]["value"] = settings["git_url"]
    # template["parameters"][2]["value"] = settings["git_ref"]
    # template["parameters"][4]["value"] = settings["min_cpu"]
    # template["parameters"][5]["value"] = settings["max_cpu"]
    # template["parameters"][6]["value"] = settings["min_memory"]
    # template["parameters"][7]["value"] = settings["max_memory"]

    # url = "{0}/apis/template.openshift.io/v1/namespaces/{1}/templateinstances"
    # url = url.format(settings["openshift_api_url"], settings["openshift_api_namespace"])

    response = requests.post("{0}/oapi/v1/namespaces/{1}/imagestreams".format(settings["openshift_api_url"], settings["openshift_api_namespace"]),
                             data=json.dumps(template_image), 
                             headers={"Authorization": "Bearer " + settings["openshift_api_token"]},
                             verify=False)
    print(str(response.text))
    response = requests.post("{0}/oapi/v1/namespaces/{1}/buildconfigs".format(settings["openshift_api_url"], settings["openshift_api_namespace"]), 
                             data=json.dumps(template_build), 
                             headers={"Authorization": "Bearer " + settings["openshift_api_token"]},
                             verify=False)
    print(str(response.text))
    response = requests.post("{0}/oapi/v1/namespaces/{1}/deploymentconfigs".format(settings["openshift_api_url"], settings["openshift_api_namespace"]),
                            data=json.dumps(template_deployment), 
                            headers={"Authorization": "Bearer " + settings["openshift_api_token"]},
                            verify=False)
    print(str(response.text))


    # resp_json = json.loads(response.text)

    # if "status" in resp_json and resp_json["status"] == "Failure":
    #     raise CreationError("Could not create object." + "\nErrorObject: " + str(resp_json))

    return True
