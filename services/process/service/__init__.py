''' Process Service  '''

from os import environ
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

DB = SQLAlchemy()
MIGRATE = Migrate()

def create_service():
    ''' Create EODC Process Registry '''

    service = Flask(__name__)

    service_settings = environ.get('SERVICE_SETTINGS')
    service.config.from_object(service_settings)

    DB.init_app(service)
    MIGRATE.init_app(service, DB)

    from service.api.health import HEALTH_BLUEPRINT
    from service.api.process import PROCESS_BLUEPRINT
    service.register_blueprint(HEALTH_BLUEPRINT)
    service.register_blueprint(PROCESS_BLUEPRINT)

    return service
