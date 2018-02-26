''' Unit Tests for Testing Config '''

from os import environ
from flask_testing import TestCase
from service import create_service

SERVICE = create_service()

class TestTestingConfig(TestCase):
    ''' Tests for Testing Config '''

    def create_app(self):
        ''' Create service with config '''

        SERVICE.config.from_object("service.config.TestingConfig")
        return SERVICE

    def test_testing_config(self):
        ''' Test for Testing Config '''

        self.assertTrue(SERVICE.config['DEBUG'])
        self.assertTrue(SERVICE.config['TESTING'])
