''' Configurations for Process Service '''

from os import environ

class BaseConfig:
    ''' Base Configuration '''
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENEO_API = environ.get("OPENEO_API_HOST")

class DevelopmentConfig(BaseConfig):
    ''' Development Configuration '''
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')

class TestingConfig(BaseConfig):
    ''' Testing Configuration '''
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_TEST_URL')

class ProductionConfig(BaseConfig):
    ''' Production Configuration '''
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
