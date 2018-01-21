''' Configurations for EODC Job Service '''

from os import environ

class BaseConfig:
    ''' Base Configuration '''
    DEBUG = False
    TESTING = False
    PUBLIC_NAMESPACE = "sandbox"
    PROCESS_REGISTRY = "http://localhost:9001"
    BUILD_CONTROLLER = "http://localhost:9002"
    DEPLOY_CONTROLLER = "http://localhost:9003"

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
