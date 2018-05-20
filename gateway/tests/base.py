''' Base Unit Tests '''

import json
from flask_testing import TestCase
from service import create_app, db
from service.tests.utils import add_user, id_generator, add_random_user

app = create_app()

class BaseTestCase(TestCase):
    ''' Base class for unit tests. '''

    def create_app(self):
        ''' Create an app instance with the testing config. '''

        app.config.from_object('service.config.TestingConfig')
        return app

    def setUp(self):
        ''' Setup the database. '''

        db.create_all()
        db.session.commit()

    def tearDown(self):
        ''' Tear down the database. '''

        db.session.remove()
        db.drop_all()

    def send_get(self, path, headers=dict()):
        ''' Helper for sending GET requests '''

        with self.client:
            response = self.client.get(path, headers=headers)
            data = json.loads(response.data.decode())

        return response, data

    def send_post(self, path, user, headers=dict()):
        ''' Helper for sending POST requests '''

        with self.client:
            response = self.client.post(
                            path,
                            data=json.dumps(user),
                            headers=headers,
                            content_type="application/json")

            data = json.loads(response.data.decode())

        return response, data

    def send_delete(self, path, headers=dict()):
        ''' Helper for sending DELETE requests '''

        with self.client:
            response = self.client.delete(path, headers=headers)
            data = json.loads(response.data.decode())

        return response, data

    def get_user_and_auth(self, permission="user"):
        ''' Helper for getting the header with auth token '''

        if permission == "admin":
            user = add_random_user(admin=True)
        else:
            user = add_random_user()

        credentials = dict(username=user.username, password="test")
        _, login_data = self.send_post("/auth/login", credentials)

        return user, dict(Authorization="Bearer " + login_data["data"]["auth_token"])
