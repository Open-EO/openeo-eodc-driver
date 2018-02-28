''' Configurations for User Service '''

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
    SQLALCHEMY_DATABASE_URI = "postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.format(
        DB_USER=environ.get("DB_USER"),
        DB_PASSWORD=environ.get("DB_PASSWORD"),
        DB_HOST=environ.get("DB_HOST"),
        DB_PORT=environ.get("DB_PORT"),
        DB_NAME=environ.get("DB_NAME"),
    )

class DevelopmentConfig(BaseConfig):
    ''' Development Configuration '''
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4

class TestingConfig(BaseConfig):
    ''' Testing Configuration '''
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    TOKEN_EXPIRATION_DAYS = 0
    TOKEN_EXPIRATION_SECONDS = 3
    SQLALCHEMY_DATABASE_URI = BaseConfig.SQLALCHEMY_DATABASE_URI + "_test"

class ProductionConfig(BaseConfig):
    ''' Production Configuration '''
    DEBUG = False
