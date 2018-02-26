import os
import unittest
from flask import current_app
from flask_testing import TestCase
from service import create_app


app = create_app()


class TestDevelopmentConfig(TestCase):
    ''' Tests for development config. '''

    def create_app(self):
        ''' Create an app instance. '''

        app.config.from_object('service.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        ''' Test correctness of development config attributes. '''

        self.assertTrue(app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY'))
        self.assertTrue(app.config['DEBUG'] is True)
        self.assertFalse(current_app is None)
        self.assertTrue(app.config['SQLALCHEMY_DATABASE_URI'] == os.environ.get('DATABASE_URL'))
        self.assertTrue(app.config['BCRYPT_LOG_ROUNDS'] == 4)
        self.assertTrue(app.config['TOKEN_EXPIRATION_DAYS'] == 30)
        self.assertTrue(app.config['TOKEN_EXPIRATION_SECONDS'] == 0)


if __name__ == '__main__':
    unittest.main()
