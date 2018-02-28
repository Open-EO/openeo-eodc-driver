''' Configurations for Data Service '''

from os import environ
from re import match

class BaseConfig:
    ''' Base Configuration '''
    DEBUG = False
    TESTING = False
    OPENEO_API = environ.get("OPENEO_API_HOST")
    if not match(r"^http(s)?:\/\/", OPENEO_API):
        OPENEO_API = "http://" + OPENEO_API

class DevelopmentConfig(BaseConfig):
    ''' Development Configuration '''
    DEBUG = False

class TestingConfig(BaseConfig):
    ''' Testing Configuration '''
    DEBUG = True
    TESTING = True

class ProductionConfig(BaseConfig):
    ''' Production Configuration '''
    DEBUG = False
