''' EODC Job Service  '''

from os import getenv
from flask import Flask
from flask_cors import CORS

def create_service():
    ''' Create EODC Job Service '''

    service = Flask(__name__)
    CORS(service)

    service_settings = getenv('SERVICE_SETTINGS')
    service.config.from_object(service_settings)

    from service.api.health import HEALTH_BLUEPRINT
    from service.api.jobs import JOBS_BLUEPRINT
    service.register_blueprint(HEALTH_BLUEPRINT)
    service.register_blueprint(JOBS_BLUEPRINT)

    return service
