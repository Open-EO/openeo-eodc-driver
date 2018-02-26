''' Unit Tests for Development Config '''

from os import environ
from flask_testing import TestCase
from service import create_service

SERVICE = create_service()

class TestDevelopmentConfig(TestCase):
    ''' Tests for Development Config '''

    def create_app(self):
        ''' Create service with config '''

        SERVICE.config.from_object("service.config.DevelopmentConfig")
        return SERVICE

    def test_development_config(self):
        ''' Test for Development Config '''

        self.assertTrue(SERVICE.config['DEBUG'])
        self.assertFalse(SERVICE.config['TESTING'])
