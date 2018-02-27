''' User Service '''

from os import environ
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

DB = SQLAlchemy()
MIGRATE = Migrate()
BCRYPT = Bcrypt()

def create_service():
    ''' Creates the service and initates the routes. '''

    service = Flask(__name__)
    service.config.from_object(environ.get('SERVICE_SETTINGS'))

    DB.init_app(service)
    BCRYPT.init_app(service)
    MIGRATE.init_app(service, DB)

    from service.api.health import HEALTH_BLUEPRINT
    from service.api.users import USERS_BLUEPRINT
    from service.api.auth import AUTH_BLUEPRINT

    service.register_blueprint(HEALTH_BLUEPRINT)
    service.register_blueprint(USERS_BLUEPRINT)
    service.register_blueprint(AUTH_BLUEPRINT)

    return service
