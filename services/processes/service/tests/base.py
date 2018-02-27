''' Base Unit Tests '''

from json import loads, dumps
from flask_testing import TestCase
from service import create_service

SERVICE = create_service()

class BaseTestCase(TestCase):
    ''' Base Class for Unit Tests '''

    def create_app(self):
        ''' Create Service '''

        SERVICE.config.from_object('service.config.TestingConfig')
        return SERVICE

    def send_get(self, path, headers=None):
        ''' Sending GET Requests '''

        if headers is None:
            headers = dict()

        with self.client:
            response = self.client.get(path, headers=headers)
            payload = loads(response.data.decode())

        return response, payload

    def send_post(self, path, data, headers=None):
        ''' Sending POST Requests '''

        if headers is None:
            headers = dict()

        with self.client:
            response = self.client.post(path,
                                        data=dumps(data),
                                        headers=headers,
                                        content_type="application/json")
            payload = loads(response.data.decode())

        return response, payload
