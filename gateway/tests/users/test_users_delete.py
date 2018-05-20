import json
import datetime

from service import db
from service.model.user import User
from service.tests.base import BaseTestCase
from service.tests.utils import add_user, id_generator, add_random_user


class TestUserServiceGET(BaseTestCase):
    ''' Tests for DELETE on Users Service. '''

    def test_delete_user_by_admin(self):  
        ''' Ensure an admin can delete a user. '''

        new_user = add_random_user()
        _, auth = self.get_user_and_auth(permission="admin")

        response, data = self.send_delete("/users/" + str(new_user.id), headers=auth)

        self.assertEqual(response.status_code, 200)
        self.assertIn(new_user.username + " successfully deleted.", data['message'])
        self.assertIn('success', data['status'])

    def test_delete_user_by_user(self):  
        ''' Ensure an user can not delete a user. '''

        new_user = add_random_user()
        _, auth = self.get_user_and_auth(permission="user")

        response, data = self.send_delete("/users/" + str(new_user.id), headers=auth)

        self.assertTrue(data["status"] == "error")
        self.assertTrue(data["message"] == "You don't have the necessary permissions.")
        self.assertEqual(response.status_code, 401)

    def test_delete_user_invalid_id(self):
        ''' Ensure error is thrown if no user id is provided. '''

        _, auth = self.get_user_and_auth(permission="admin")

        response, data = self.send_delete("/users/asdfsaf", headers=auth)

        self.assertEqual(response.status_code, 404)
        self.assertIn('User does not exist.', data['message'])
        self.assertIn('not found', data['status'])

    def test_delete_user_id_not_exists(self):
        ''' Ensure error is thrown if invalid user id is provided / user does not exist. '''

        _, auth = self.get_user_and_auth(permission="admin")

        response, data = self.send_delete("/users/999999999999999999999", headers=auth)

        self.assertEqual(response.status_code, 404)
        self.assertIn('User does not exist.', data['message'])
        self.assertIn('not found', data['status'])