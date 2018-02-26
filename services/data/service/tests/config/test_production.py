''' Unit Tests for Production Config '''

from os import environ
from flask_testing import TestCase
from service import create_service

SERVICE = create_service()

class TestProductionConfig(TestCase):
    ''' Tests for Production Config '''

    def create_app(self):
        ''' Create service with config '''

        SERVICE.config.from_object("service.config.ProductionConfig")
        return SERVICE

    def test_production_config(self):
        ''' Test for Production Config '''

        self.assertFalse(SERVICE.config['DEBUG'])
        self.assertFalse(SERVICE.config['TESTING'])
