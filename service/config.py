''' Configurations for EODC Job Service '''

from os import environ

class BaseConfig:
    ''' Base Configuration '''
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NAMESPACE = "execution-environment"

class DevelopmentConfig(BaseConfig):
    ''' Development Configuration '''
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
    OPENEO_API = "http://openeo.eodc.eu"

class TestingConfig(BaseConfig):
    ''' Testing Configuration '''
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_TEST_URL')
    OPENEO_API = "http://openeo.eodc.eu"

class ProductionConfig(BaseConfig):
    ''' Production Configuration '''
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
    OPENEO_API = ""
