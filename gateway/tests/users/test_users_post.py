from tests.base import BaseTestCase
from tests.utils import get_random_user_dict


class TestUserServicePOST(BaseTestCase):
    """ Tests for POST on users service. """

    def test_admin_add_user(self):
        """ Ensure that admin has permissions to add user """

        admin, auth = self.get_basic_user_and_auth(permission="admin")
        new_user = get_random_user_dict()

        response, data = self.send_post("/v1.0/users_mng/users", new_user, headers=auth)

        self.assertEqual(response.status_code, 201)
        self.assertIn(f"User {new_user['username']} successfully registered.", data['message'])

    def test_admin_add_user_no_admin(self):
        """ Ensure that user has permissions to add user """

        _, auth = self.get_basic_user_and_auth(permission="user")
        new_user = get_random_user_dict()

        response, data = self.send_post("/v1.0/users_mng/users", new_user, headers=auth)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(data["message"] == "You don't have the necessary permissions.")

    def test_post_user_empty_json(self):
        """ Ensure error is thrown if the JSON object is empty. """

        _, auth = self.get_basic_user_and_auth(permission="admin")

        response, data = self.send_post("/users", dict(), headers=auth)

        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid payload.', data['message'])
        self.assertIn('error', data['status'])

    def test_post_user_no_username(self):
        """ Ensure error is thrown if the JSON object does not have a username. """

        _, auth = self.get_basic_user_and_auth(permission="admin")

        user = get_random_user_dict(username=False)
        response, data = self.send_post("/users", user, headers=auth)

        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid payload.', data['message'])
        self.assertIn('error', data['status'])

    def test_post_user_no_email(self):
        """ Ensure error is thrown if the JSON object does not have a email. """

        _, auth = self.get_basic_user_and_auth(permission="admin")

        user = get_random_user_dict(email=False)
        response, data = self.send_post("/users", user, headers=auth)

        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid payload.', data['message'])
        self.assertIn('error', data['status'])

    def test_post_user_no_password(self):
        """ Ensure error is thrown if the JSON object does not have a password. """

        _, auth = self.get_basic_user_and_auth(permission="admin")

        user = get_random_user_dict(password=False)
        response, data = self.send_post("/users", user, headers=auth)

        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid payload.', data['message'])
        self.assertIn('error', data['status'])

    def test_post_user_duplicate_username(self):
        """ Ensure error is thrown if the username already exists. """

        _, auth = self.get_basic_user_and_auth(permission="admin")

        user_1 = get_random_user_dict()
        user_2 = get_random_user_dict()

        user_2["username"] = user_1["username"]

        _, _ = self.send_post("/users", user_1, headers=auth)
        response, data = self.send_post("/users", user_2, headers=auth)

        self.assertEqual(response.status_code, 400)
        self.assertIn('The username already exists.', data['message'])
        self.assertIn('error', data['status'])

    def test_post_user_duplicate_email(self):
        """ Ensure error is thrown if the email already exists. """

        _, auth = self.get_basic_user_and_auth(permission="admin")

        user_1 = get_random_user_dict()
        user_2 = get_random_user_dict()

        user_2["email"] = user_1["email"]

        _, _ = self.send_post("/users", user_1, headers=auth)
        response, data = self.send_post("/users", user_2, headers=auth)

        self.assertEqual(response.status_code, 400)
        self.assertIn('The e-mail already exists.', data['message'])
        self.assertIn('error', data['status'])
