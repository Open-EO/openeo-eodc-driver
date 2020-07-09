""" Base Unit Tests """
import base64
import json

from flask_testing import TestCase

from gateway import gateway
from gateway.users.models import db
from tests.utils import add_random_basic_user, add_random_profile


class BaseTestCase(TestCase):
    """ Base class for unit tests. """

    def create_app(self):
        """ Create an app instance with the testing config. """
        app = gateway.get_service()
        return app

    def setUp(self):
        """ Create database tables """
        db.create_all()

    def tearDown(self):
        """ Empty and drop database """
        db.session.remove()
        db.drop_all()

    def send_get(self, path: str, headers: dict = None):
        """ Helper for sending GET requests """
        headers = headers if headers else {}

        with self.client:
            response = self.client.get(path, headers=headers)
            data = json.loads(response.data.decode())

        return response, data

    def send_post(self, path, user, headers: dict = None):
        """ Helper for sending POST requests """
        headers = headers if headers else {}

        with self.client:
            response = self.client.post(
                path,
                data=json.dumps(user),
                headers=headers,
                content_type="application/json")

            data = json.loads(response.data.decode())

        return response, data

    def send_delete(self, path, headers: dict = None):
        """ Helper for sending DELETE requests """
        headers = headers if headers else {}

        with self.client:
            response = self.client.delete(path, headers=headers)
            data = json.loads(response.data.decode())

        return response, data

    def get_basic_user_and_auth(self, permission="user", profile: bool = True):
        """ Helper for getting the header with auth token """

        profile = add_random_profile()
        if permission == "admin":
            user = add_random_basic_user(role="admin", profile_id=profile.id)
        else:
            user = add_random_basic_user(profile_id=profile.id)

        # create binary literals for base64 encoding and afterwards decode it again to string
        credentials = base64.b64encode(f"{user.username}:test".encode("utf-8")).decode("utf-8")
        header = {"Authorization": f"Basic {credentials}"}
        _, login_data = self.send_get("/v1.0/credentials/basic", headers=header)
        return user, {"Authorization": f"Bearer basic//{login_data['access_token']}"}
