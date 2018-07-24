''' Base Class for OpenShift Templates '''

from abc import ABC, abstractmethod
from json import dumps
from ..api_connector import APIConnectionError

class TemplateError(Exception):
    ''' Template Exception raises if the template could not be parsed or excecuted. '''
    def __init__(self, code, msg=None):
        if not msg:
            msg = "Error while parsing templates."
        super(TemplateError, self).__init__(msg)
        self.code = code

class BaseTemplate(ABC):
    ''' Base Class for OpenShift Templates '''

    def __init__(self, template_id, path, kind, api_version):
        self.template_id = template_id
        self.selfLinks = {
            "base": path,
            "template": "{0}/{1}".format(path, template_id)
        }

        self.template = {
            "kind": kind,
            "apiVersion": api_version,
            "metadata": {
                "name": self.template_id
            }
        }
    
    def create(self, api_connector, watch=True):
        ''' Create the template object '''
        try:
            response = api_connector.request("openshift", "post", self.selfLinks["base"], self.get_json())
            self.extract_selfLinks(response, api_connector)

            if watch:
                self.is_ready(api_connector)
            
            return self
        except APIConnectionError as exp:
            if not exp.code == 409:
                raise
            self.delete(api_connector)
            self.create(api_connector)
            return self
            

    def delete(self, api_connector):
        ''' Delete the template and pod '''
        api_connector.request("openshift", "delete", self.selfLinks["template"])
        if "pod" in self.selfLinks:
            api_connector.request("openshift", "delete", self.selfLinks["pod"])
    
    def exists(self, api_connector):
        try:
            response = api_connector.request("openshift", "get", self.selfLinks["template"])
            self.extract_selfLinks(response, api_connector)
            return True
        except APIConnectionError:
            return False

    def get_json(self):
        ''' Return template as JSON '''
        return dumps(self.template)

    @abstractmethod
    def is_ready(self, response):
        pass
    
    @abstractmethod
    def extract_selfLinks(self, response, api_connector):
        pass
