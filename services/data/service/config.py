''' Configurations for Data Service '''

class BaseConfig:
    ''' Base Configuration '''
    DEBUG = False
    TESTING = False
    OPENEO_API = "http://openeo.eodc.eu"

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
