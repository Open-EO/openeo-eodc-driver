from sqlalchemy.exc import IntegrityError
from service import db
from service.model.user import User
from service.tests.base import BaseTestCase
from service.tests.utils import add_random_user


class TestUserModel(BaseTestCase):
    ''' Tests for the User model '''

    def test_add_user(self):
        ''' Ensures the User model is correct '''

        user = add_random_user()
        
        self.assertTrue(user.id)
        self.assertEqual(user.username, user.username)
        self.assertEqual(user.email,  user.email)
        self.assertTrue(user.password)
        self.assertTrue(user.active)
        self.assertTrue(user.created_at)
        self.assertFalse(user.admin)

    def test_add_user_duplicate_username(self):
        ''' Ensure an exception is thrown if user with existing username is added '''

        user_1 = add_random_user()
        user_2 = User(username=user_1.username,
                      email="test_user22@eodc.eu",
                      password="test")

        db.session.add(user_2)

        self.assertRaises(IntegrityError, db.session.commit)

    def test_add_user_duplicate_email(self):
        ''' Ensure an exception is thrown if user with existing email is added '''

        user_1 = add_random_user()
        user_2 = User(username="test_user_2",
                      email=user_1.email,
                      password="test")
    
        db.session.add(user_2)

        self.assertRaises(IntegrityError, db.session.commit)
