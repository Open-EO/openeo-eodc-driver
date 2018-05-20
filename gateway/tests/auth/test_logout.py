import json
import time
from service import db
from service.model.user import User
from service.tests.base import BaseTestCase
from service.tests.utils import add_random_user


class TestAuthLogout(BaseTestCase):
    ''' Tests for User Logout '''

    def test_valid_logout(self):
        ''' Ensure that the user can logout. '''

        user = add_random_user()

        credentials = dict(username=user.username, password="test")
        _, login_data = self.send_post("/auth/login", credentials)
        
        auth = dict(Authorization='Bearer ' + login_data["data"]["auth_token"])
        response, data = self.send_get("/auth/logout", headers=auth)

        self.assertTrue(login_data['status'] == 'success')
        self.assertTrue(data['message'] == 'Successfully logged out.')
        self.assertEqual(response.status_code, 200)

    # def test_invalid_logout_expired_token(self):
    #     ''' Ensure that a error is thrown if the token expired. '''

    #     user = add_random_user()

    #     credentials = dict(username=user.username, password="test")
    #     _, login_data = self.send_post("/auth/login", credentials)

    #     time.sleep(4)

    #     auth = dict(Authorization='Bearer ' + login_data["data"]["auth_token"])
    #     response, data = self.send_get("/auth/logout", headers=auth)

    #     self.assertTrue(data['status'] == 'error')
    #     self.assertTrue(data['message'] == 'Signature expired. Please log in again.')
    #     self.assertEqual(response.status_code, 401)

    def test_invalid_logout(self):
        ''' Ensure that an error is thrown if an invalid token is send. '''

        auth = dict(Auth='Bearer invalid')
        response, data = self.send_get("/auth/logout", headers=auth)

        self.assertTrue(data['status'] == "error")
        self.assertTrue(data['message'] == "Provide a valid auth token.")
        self.assertEqual(response.status_code, 403)
