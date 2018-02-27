''' Data Service  '''

from os import getenv
from flask import Flask
from owslib.csw import CatalogueServiceWeb

def create_service():
    ''' Create service '''

    service = Flask(__name__)

    service_settings = getenv('SERVICE_SETTINGS')
    service.config.from_object(service_settings)

    from service.api.health import HEALTH_BLUEPRINT
    from service.api.data import DATA_BLUEPRINT
    from service.api.products import PRODUCTS_BLUEPRINT
    service.register_blueprint(HEALTH_BLUEPRINT)
    service.register_blueprint(DATA_BLUEPRINT)
    service.register_blueprint(PRODUCTS_BLUEPRINT)

    return service
