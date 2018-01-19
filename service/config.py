''' Application Configurations '''
import os


class BaseConfig:
    ''' Base Configuration '''

    DEBUG = False
    TESTING = False
    OPENSHIFT_API_URL = "https://openshift-master.eodc.eu:443"
    OPENSHIFT_API_TOKEN = "mIWAQ9Ll2HOtr4mToclCEq_hCuhLIxLjaCOcvxsW99U"
    OPENSHIFT_API_NAMESPACE = "sandbox"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    ''' Development Configuration '''
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('POSTGRES_URL')
    CELERY_BROKER_URL = os.environ.get('REDIS_URL')
    CELERY_RESULT_BACKEND = os.environ.get('POSTGRES_URL')

class TestingConfig(BaseConfig):
    ''' Testing Configuration '''
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('POSTGRES_TEST_URL')
    CELERY_BROKER_URL = os.environ.get('REDIS_URL')
    CELERY_RESULT_BACKEND = os.environ.get('POSTGRES_TEST_URL')


class ProductionConfig(BaseConfig):
    ''' Production Configuration '''
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('POSTGRES_URL')
    CELERY_BROKER_URL = os.environ.get('REDIS_URL')
    CELERY_RESULT_BACKEND = os.environ.get('POSTGRES_URL')
