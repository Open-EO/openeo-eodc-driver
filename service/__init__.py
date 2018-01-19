''' Benchmark Service '''

import os
from flask  import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app():
    ''' Create Flask App '''

    app = Flask(__name__)
    CORS(app)

    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    db.init_app(app)

    from service.api.health import HEALTH_BLUEPRINT
    from service.api.jobs import JOBS_BLUEPRINT
    app.register_blueprint(HEALTH_BLUEPRINT)
    app.register_blueprint(JOBS_BLUEPRINT)

    return app
