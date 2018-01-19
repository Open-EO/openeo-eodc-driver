''' Base Test Case '''

import json
from flask_testing import TestCase
from service import create_app, db


APP = create_app()


class BaseTestCase(TestCase):
    ''' Base class for unit tests. '''

    def create_app(self):
        ''' Create an app instance with the testing config. '''

        APP.config.from_object('service.config.TestingConfig')
        return APP

    def setUp(self):
        ''' Setup the database. '''

        db.create_all()
        db.session.commit()

    def tearDown(self):
        ''' Tear down the database. '''

        db.session.remove()
        db.drop_all()

    def send_get(self, path, headers=None):
        ''' Helper for sending GET requests '''

        if headers is None:
            headers = dict()

        with self.client:
            response = self.client.get(path, headers=headers)
            data = json.loads(response.data.decode())

        return response, data

    def send_post(self, path, data, headers=None):
        ''' Helper for sending POST requests '''

        if headers is None:
            headers = dict()

        with self.client:
            response = self.client.post(path,
                                        data=json.dumps(data),
                                        headers=headers,
                                        content_type="application/json")

            data = json.loads(response.data.decode())

        return response, data
