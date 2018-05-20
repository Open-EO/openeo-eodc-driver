import json
import datetime

from service import db
from service.model.user import User
from service.tests.base import BaseTestCase
from service.tests.utils import add_user, id_generator, add_random_user


class TestUserServiceGET(BaseTestCase):
    ''' Tests for GET on Users Service. '''

    def test_get_pong(self):
        ''' Ensure the availability check is working. '''

        response, data = self.send_get("/ping")

        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_get_user_own(self):  
        ''' Ensure the users can retrieve their own information. '''

        user, auth = self.get_user_and_auth(permission="user")

        response, data = self.send_get("/users/" + str(user.id), headers=auth)

        self.assertEqual(response.status_code, 200)
        self.assertIn('User found.', data['message'])
        self.assertIn('success', data['status'])
        self.assertIn(user.username, data['data']['username'])
        self.assertIn(user.email, data['data']['email'])
        self.assertEqual(user.admin, data['data']['admin'])
        self.assertTrue('created_at' in data['data'])

    def test_get_user_other(self):  
        ''' Ensure the users can bot retrieve informations of other users. '''

        new_user = add_random_user()
        user, auth = self.get_user_and_auth(permission="user")

        response, data = self.send_get("/users/" + str(new_user.id), headers=auth)

        self.assertEqual(response.status_code, 401)
        self.assertIn("You don't have the necessary permissions.", data["message"])
        self.assertIn('error', data['status'])
    
    def test_admin_get_user(self):
        ''' Ensure admin can access details of users. '''

        user = add_random_user()
        _, auth = self.get_user_and_auth(permission="admin")

        response, data = self.send_get("/users/" + str(user.id), headers=auth)

        self.assertEqual(response.status_code, 200)
        self.assertIn('User found.', data['message'])
        self.assertIn('success', data['status'])
        self.assertIn(user.username, data['data']['username'])
        self.assertIn(user.email, data['data']['email'])
        self.assertEqual(user.admin, data['data']['admin'])
        self.assertTrue('created_at' in data['data'])

    def test_get_user_invalid_id(self):
        ''' Ensure error is thrown if an id is not provided. '''
        _, auth = self.get_user_and_auth(permission="admin")

        name_gen = id_generator()
        response, data = self.send_get("/users/" + name_gen, headers=auth)

        self.assertEqual(response.status_code, 404)
        self.assertIn('User does not exist.', data['message'])
        self.assertIn('not found', data['status'])

    def test_get_user_id_not_exists(self):
        ''' Ensure error is thrown if the id does not exist. '''
        _, auth = self.get_user_and_auth(permission="admin")

        response, data = self.send_get("/users/999999999999999999", headers=auth)

        self.assertEqual(response.status_code, 404)
        self.assertIn('User does not exist.', data['message'])
        self.assertIn('not found', data['status'])

    def test_get_users_no_admin(self):
        ''' Ensure get users behaves correctly. '''

        _, auth = self.get_user_and_auth(permission="user")

        response, data = self.send_get("/users", headers=auth)

        self.assertEqual(response.status_code, 401)
        self.assertIn("You don't have the necessary permissions.", data['message'])
        self.assertIn('error', data['status'])

    def test_get_users_admin(self):
        ''' Ensure get users behaves correctly. '''

        _, auth = self.get_user_and_auth(permission="admin")

        created = datetime.datetime.utcnow() + datetime.timedelta(-30)

        user_1 = add_random_user(created_at=created)
        user_2 = add_random_user()

        response, data = self.send_get("/users", headers=auth)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['data']['users']), 3)
        self.assertIn('success', data['status'])

        self.assertIn(user_1.username, data['data']['users'][2]['username'])
        self.assertIn(user_2.username, data['data']['users'][1]['username'])

        self.assertIn(user_1.email, data['data']['users'][2]['email'])
        self.assertIn(user_2.email, data['data']['users'][1]['email'])

        self.assertEqual(user_1.admin, data['data']['users'][2]['admin'])
        self.assertEqual(user_2.admin, data['data']['users'][1]['admin'])

        self.assertTrue('created_at' in data['data']['users'][2])
        self.assertTrue('created_at' in data['data']['users'][1])
