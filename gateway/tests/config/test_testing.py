import os
import unittest
from flask import current_app
from flask_testing import TestCase
from service import create_app


app = create_app()


class TestTestingConfig(TestCase):
    ''' Tests for testing config. '''

    def create_app(self):
        ''' Create an app instance. '''

        app.config.from_object('service.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        ''' Test correctness of testing config attributes. '''

        self.assertTrue(app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY'))
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertTrue(app.config['SQLALCHEMY_DATABASE_URI'] == os.environ.get('DATABASE_TEST_URL'))
        self.assertTrue(app.config['BCRYPT_LOG_ROUNDS'] == 4)
        self.assertTrue(app.config['TOKEN_EXPIRATION_DAYS'] == 0)
        self.assertTrue(app.config['TOKEN_EXPIRATION_SECONDS'] == 3)


if __name__ == '__main__':
    unittest.main()
