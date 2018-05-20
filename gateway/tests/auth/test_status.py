import json
import time
from service import db
from service.model.user import User
from service.tests.base import BaseTestCase
from service.tests.utils import add_random_user


class TestAuthStatus(BaseTestCase):
    ''' Tests for User Status '''

    def test_user_status(self):
        ''' Ensure that the user status can be retrieved '''

        user, auth = self.get_user_and_auth(permission="user")

        response, data = self.send_get("/auth/status", headers=auth)

        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['data'] is not None)
        self.assertTrue(data['data']['username'] == user.username)
        self.assertTrue(data['data']['email'] == user.email)
        self.assertTrue(data['data']['active'])
        self.assertTrue(data['data']['created_at'])
        self.assertEqual(response.status_code, 200)

    def test_invalid_status(self):
        ''' Ensure that an error is thrown if an invalid token was send. '''

        auth = dict(Auth='Bearer invalid')
        response, data = self.send_get("/auth/status", headers=auth)

        self.assertTrue(data['status'] == 'error')
        self.assertTrue(data['message'] == "Provide a valid auth token.")
        self.assertEqual(response.status_code, 403)