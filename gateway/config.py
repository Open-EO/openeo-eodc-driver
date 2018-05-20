''' Configurations for User Service '''

from os import environ

class BaseConfig:
    ''' Base Configuration '''
    DEBUG = False
    TESTING = False
    # CORS_ENABLED = True

class DevelopmentConfig(BaseConfig):
    ''' Development Configuration '''
    DEBUG = True

class TestingConfig(BaseConfig):
    ''' Testing Configuration '''
    DEBUG = True
    TESTING = True

class ProductionConfig(BaseConfig):
    ''' Production Configuration '''
    DEBUG = False
