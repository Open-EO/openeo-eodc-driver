from sqlalchemy.exc import IntegrityError
from service import db
from service.model.user import User
from service.tests.base import BaseTestCase
from service.tests.utils import add_random_user, add_user


class TestEncryption(BaseTestCase):
    ''' Tests for the password encryption '''

    def test_passwords_are_random(self):
        ''' Ensure equal passwords are encrypted randomly. '''

        user_1 = add_random_user()
        user_2 = add_random_user()

        self.assertNotEqual(user_1.password, user_2.password)
    
    def test_encode_auth_token(self):
        ''' Ensure the auth token behaves correctly. '''

        user = add_random_user()
        auth_token = user.encode_auth_token(user.id)

        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        ''' Ensure the decrypted auth token includes the correct user id. '''

        user = add_random_user()
        auth_token = user.encode_auth_token(user.id)

        self.assertEqual(user.decode_auth_token(auth_token), user.id)
