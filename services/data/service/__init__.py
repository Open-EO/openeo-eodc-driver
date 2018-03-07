''' Data Service  '''

from os import getenv
from flask import Flask

def create_service():
    ''' Create service '''

    service = Flask(__name__)

    service_settings = getenv('SERVICE_SETTINGS')
    service.config.from_object(service_settings)

    from service.api.main import MAIN_BLUEPRINT
    from service.api.health import HEALTH_BLUEPRINT
    from service.api.data import DATA_BLUEPRINT
    from service.api.capabilities import CAPABILITIES_BLUEPRINT
    service.register_blueprint(MAIN_BLUEPRINT)
    service.register_blueprint(HEALTH_BLUEPRINT)
    service.register_blueprint(DATA_BLUEPRINT)
    service.register_blueprint(CAPABILITIES_BLUEPRINT)

    return service
