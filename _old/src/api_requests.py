''' Kubernetes / OpenShift objects creation '''

import json
import requests
from flask import current_app


class CreationError(Exception):
    ''' Error class for expections retrieved by OpenShift '''
    pass


def create_object(config_json, obj, api="oapi", parameters=()):
    ''' Helper function for creating Kubernetes / OpenShift objects '''

    with open("./service/src/templates/" + config_json) as json_file:
        data = json_file.read().replace(" ", "").replace("\n", "")
        data = data % parameters

        url = "{0}/{1}/v1/namespaces/{2}/{3}".format(current_app.config.get('SERVER_IP'), api, current_app.config.get('NAMESPACE'), obj)
        response = requests.post(url, data=data, headers=current_app.config.get('AUTH'), verify=current_app.config.get('VERIFY'))
        print(response.text)
        resp_json = json.loads(response.text)
        if "status" in resp_json and resp_json["status"] == "Failure":
            raise CreationError("Could not create object." + "\nErrorObject: " + str(resp_json))


def patch_object(config_json, obj, selector, api="oapi", parameters=()):
    ''' Helper function for updating Kubernetes / OpenShift objects '''

    with open("./service/src/templates/" + config_json) as json_file:
        data = json_file.read().replace(" ", "").replace("\n", "")
        data = data % parameters

        url = "{0}/{1}/v1/namespaces/{2}/{3}/{4}".format(current_app.config.get('SERVER_IP'), api, current_app.config.get('NAMESPACE'), obj, selector)
        response = requests.patch(url, data=data, headers=current_app.config.get('AUTH'), verify=current_app.config.get('VERIFY'))

        resp_json = json.loads(response.text)
        if "status" in resp_json and resp_json["status"] == "Failure":
            raise CreationError("Could not create object." +
                                "\nErrorObject: " + str(resp_json))


def delete_object(obj, selector, api="oapi"):
    ''' Helper function for deleting Kubernetes / OpenShift objects '''

    url = "{0}/{1}/v1/namespaces/{2}/{3}/{4}".format(current_app.config.get('SERVER_IP'), api, current_app.config.get('NAMESPACE'), obj, selector)
    response = requests.delete(url, headers=current_app.config.get('AUTH'), verify=current_app.config.get('VERIFY'))

    resp_json = json.loads(response.text)
    if "status" in resp_json and resp_json["status"] == "Failure":
        raise CreationError("Could not create object." +
                            "\nErrorObject: " + str(resp_json))

    print(resp_json)
