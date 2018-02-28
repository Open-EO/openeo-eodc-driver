''' Configurations for Data Service '''

from os import environ
from re import match

class BaseConfig:
    ''' Base Configuration '''
    DEBUG = False
    TESTING = False
    CSW_SERVER = environ.get("CSW_SERVER")
    if not match(r"^http(s)?:\/\/", CSW_SERVER):
        CSW_SERVER = "http://" + CSW_SERVER

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
