import os
import unittest
from flask import current_app
from flask_testing import TestCase
from service import create_app


app = create_app()


class TestProductionConfig(TestCase):
    ''' Tests for production config. '''

    def create_app(self):
        ''' Create an app instance. '''

        app.config.from_object('service.config.ProductionConfig')
        return app

    def test_app_is_production(self):
        ''' Test correctness of production config attributes. '''

        self.assertTrue(app.config['SECRET_KEY'] == os.environ.get('SECRET_KEY'))
        self.assertFalse(app.config['DEBUG'])
        self.assertFalse(app.config['TESTING'])
        self.assertTrue(app.config['BCRYPT_LOG_ROUNDS'] == 13)
        self.assertTrue(app.config['TOKEN_EXPIRATION_DAYS'] == 30)
        self.assertTrue(app.config['TOKEN_EXPIRATION_SECONDS'] == 0)


if __name__ == '__main__':
    unittest.main()
