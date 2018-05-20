from os import environ
from json import loads
from nameko.extensions import DependencyProvider
from requests import get, post, put, delete, HTTPError
# from websocket import create_connection
from time import sleep
# Just temporary (till valid certificate)
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)

from ..exceptions import APIConnectionError

class APIConnectorWrapper:
    __APIS = {
        "openshift": environ.get("OPENSHIFT_API"),
        "hawkular": environ.get("HAWKULAR_API"),
    }

    __VERBS = {
        "get": get,
        "post": post,
        "put": put,
        "delete": delete
    }

    __CONTENT_TYPES = {
        "text/plain": lambda response: response.text,
        "application/json": lambda response: loads(response.text)
    }

    __API_WATCH_SLEEP = 2
    __TIMEOUT_CONNECTION = 5
    __TIMEOUT_READ = 30

    def __init__(self):
        self.__namespace = environ.get("OPENSHIFT_PROJECT")
        self.__headers = {
            "Authorization": "Bearer " + environ.get("SA_TOKEN"),
            "Hawkular-Tenant": environ.get("OPENSHIFT_PROJECT")}
        self.__verify = True if environ.get("VERIFY") == "true" else False

    def request(self, api_name, verb_name, path, data=None):
        try:
            response = self.__VERBS[verb_name](
                self.__APIS[api_name] + path.format(self.__namespace), 
                data=data, 
                headers=self.__headers, 
                verify=self.__verify,
                timeout=(self.__TIMEOUT_CONNECTION, self.__TIMEOUT_READ))

            response.raise_for_status()

            return self.__CONTENT_TYPES[response.headers['Content-Type']](response)
        except HTTPError as exp:
            raise APIConnectionError(exp.response.status_code, loads(exp.response.text))

    def watch(self, api_name, path, data=None):
        # TODO: OPEN WEBSOCKET PORTS ???
        # api = "ws://" + self.__APIS["openshift"].split("//")[1] + ":80"
        # path = path.format(self.__namespace) + "?resourceVersion=0&watch=true"

        # a = api + path
        # ws = create_connection(api + path)
        # for result in ws.recv():
        #     print(result)
        # ws.close()
        while True:
            yield self.request(api_name, "get", path, data)
            sleep(self.__API_WATCH_SLEEP)

class APIConnector(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return APIConnectorWrapper()