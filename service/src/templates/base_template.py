''' Base for OpenShift Templates '''

from json import dumps, loads
from requests import post
from re import match
from flask import current_app
from service.src.exceptions import TemplateException

class BaseTemplate:
    ''' Base Class for OpenShift Templates '''

    def __init__(self, kind, api_version, path, validation, payload):
        self.kind = kind
        self.api_version = api_version
        self.validation = validation

        self.validation["namespace"] = r"([a-z]|-){5,}"
        self.validation["name"] = r"([a-z]|-){5,}"

        self.validate_payload(payload)
        self.vars = payload

        self.path = path.format(current_app.config["OPENSHIFT_PROJECT"])
        self.template = {
            "kind": self.kind,
            "apiVersion": self.api_version,
            "metadata": {
                "name": self.vars["name"]
            }
        }

    def validate_payload(self, payload):
        ''' Validate the values '''

        for key, value in self.validation.items():
            if not key in payload:
                raise TemplateException("Missing {0} for {1}."\
                                        .format(key, self.kind))

            if value is not None:
                if not match(value, payload[key]):
                    raise TemplateException("Value '{0}' for key '{1}' in {2} is not correct: {3}."\
                                            .format(payload[key], key, self.kind, value))

    def get_json(self):
        ''' Generates JSON from the member template '''
        return dumps(self.template)

    def execute(self):
        ''' Parses and send the template to the OpenShift API'''

        url = current_app.config["OPENSHIFT_API"] + self.path
        auth = {"Authorization": "Bearer " + current_app.config["SERVICE_TOKEN"]}
        verify = current_app.config["VERIFY"]

        response = post(url,
                        data=self.get_json(),
                        headers=auth,
                        verify=verify)

        if response.status_code != 201:
            raise TemplateException(response.text)

        response_json = loads(response.text)
        name = response_json["metadata"]["name"]
        self_link = response_json["metadata"]["selfLink"]

        return name, self_link