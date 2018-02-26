''' Configurations for EODC User Service '''

from os import environ

class BaseConfig:
    ''' Base Configuration '''
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_BCRYPT = environ.get('SECRET_BCRYPT')
    BCRYPT_LOG_ROUNDS = 13
    TOKEN_EXPIRATION_DAYS = 30
    TOKEN_EXPIRATION_SECONDS = 0

class DevelopmentConfig(BaseConfig):
    ''' Development Configuration '''
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
    BCRYPT_LOG_ROUNDS = 4

class TestingConfig(BaseConfig):
    ''' Testing Configuration '''
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_TEST_URL')
    BCRYPT_LOG_ROUNDS = 4
    TOKEN_EXPIRATION_DAYS = 0
    TOKEN_EXPIRATION_SECONDS = 3

class ProductionConfig(BaseConfig):
    ''' Production Configuration '''
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
