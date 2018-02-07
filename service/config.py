''' Configurations for EODC Job Service '''

from os import environ

class BaseConfig:
    ''' Base Configuration '''
    DEBUG = False
    TESTING = False
    NAMESPACE = "sandbox"
    OPENEO_API = "http://openeo.eodc.eu"

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
