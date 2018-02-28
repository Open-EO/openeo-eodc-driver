''' Configurations for Job Service '''

from os import environ
from re import match

class BaseConfig:
    ''' Base Configuration '''
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NAMESPACE = environ.get("EXECUTION_NAMESPACE")

    OPENEO_API = environ.get("OPENEO_API_HOST")
    if not match(r"^http(s)?:\/\/", OPENEO_API):
        OPENEO_API = "http://" + OPENEO_API
        
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

class TestingConfig(BaseConfig):
    ''' Testing Configuration '''
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = BaseConfig.SQLALCHEMY_DATABASE_URI + "_test"

class ProductionConfig(BaseConfig):
    ''' Production Configuration '''
    DEBUG = False
