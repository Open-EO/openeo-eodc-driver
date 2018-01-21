''' Configurations for EODC Job Service '''

from os import environ

class BaseConfig:
    ''' Base Configuration '''
    DEBUG = False
    TESTING = False
    PUBLIC_NAMESPACE = "sandbox"
    PROCESS_REGISTRY = "http://localhost:9001"

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
