import json
import time
from service import db
from service.model.user import User
from service.tests.base import BaseTestCase
from service.tests.utils import add_random_user


class TestAuthLogin(BaseTestCase):
    ''' Tests for User Login '''

    def test_post_user_login(self):
        ''' Ensure that a user that exists in the database and can log in '''

        user = add_random_user()
        credentials = dict(username=user.username, password="test")

        response, data = self.send_post("/auth/login", credentials)

        self.assertTrue(data["status"] == "success")
        self.assertTrue(data["message"] == "Successfully logged in.")
        self.assertTrue(data["data"]["auth_token"])
        self.assertFalse(data["data"]["admin"])
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 200)

    def test_post_admin_login(self):
        ''' Ensure that a dmin can login and gets permissions '''

        user = add_random_user(admin=True)
        credentials = dict(username=user.username, password="test")

        response, data = self.send_post("/auth/login", credentials)

        self.assertTrue(data["status"] == "success")
        self.assertTrue(data["message"] == "Successfully logged in.")
        self.assertTrue(data["data"]["auth_token"])
        self.assertTrue(data["data"]["admin"])
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 200)

    def test_not_registered_user_login(self):
        ''' Ensure that a user that does not exist in the database and can not log in '''
        
        not_user = dict(username="not registered", password="test")
        response, data = self.send_post("/auth/login", not_user)

        self.assertTrue(data['status'] == "not found")
        self.assertTrue(data['message'] == "User does not exist.")
        self.assertTrue(response.content_type == "application/json")
        self.assertEqual(response.status_code, 404)
