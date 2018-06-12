from os import environ
from flask import Flask, redirect, current_app
from flask_cors import CORS
from flask_nameko import FlaskPooledClusterRpcProxy
from flask_restful_swagger_2 import Api, swagger

rpc = FlaskPooledClusterRpcProxy()


def create_gateway():

    gateway = Flask(__name__)
    CORS(gateway, resources={r"/api/*": {"origins": "*"}})

    gateway.config.from_object(environ.get('GATEWAY_SETTINGS'))
    gateway.config.update(
        dict(
            NAMEKO_AMQP_URI="pyamqp://{0}:{1}@{2}:{3}".format(
                environ.get("RABBIT_USER"),
                environ.get("RABBIT_PASSWORD"),
                environ.get("RABBIT_HOST"),
                environ.get("RABBIT_PORT")
            )
        )
    )

    rpc.init_app(gateway)
    generate_api(gateway)

    return gateway


def generate_api(gateway):
    api = Api(
        gateway,
        api_version='0.0.2',
        host="127.0.0.1:3000",
        title="EODC openEO API",
        description="EODC API implementation of openEO",
        contact={
            "name": "EODC",
            "url": "http://eodc.eu",
            "email": "gunnar.busch@eodc.eu"
        },
        consumes=[
            "application/json"
        ],
        produces=[
            "application/json"
        ],
        schemes=[
            "http",
            "https"
        ],
        security_definitions={
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header"
            },
            "Basic": {
                "type": "basic"
            }
        }
    )

    from .index import Index
    from .health import HealthApi, ServiceHealthApi
    from .auth import RegisterApi, LoginApi
    from .data import RecordsApi, ProductDetailApi
    from .processes import ProcessApi, ProcessDetailApi
    from .jobs import JobsApi, JobDetailApi,BatchJobApi, DownloadApi, DownloadFileApi

    api.add_resource(Index, "/")
    api.add_resource(HealthApi, "/health")
    api.add_resource(ServiceHealthApi, "/health/services")
    api.add_resource(RegisterApi, "/auth/register")
    api.add_resource(LoginApi, "/auth/login")
    api.add_resource(RecordsApi, "/data")
    api.add_resource(ProductDetailApi, "/data/<string:product_id>")
    api.add_resource(ProcessApi, "/processes")
    api.add_resource(ProcessDetailApi, "/processes/<string:process_id>")
    api.add_resource(JobsApi, "/jobs")
    api.add_resource(JobDetailApi, "/jobs/<string:job_id>")
    api.add_resource(BatchJobApi, "/jobs/<string:job_id>/queue")
    api.add_resource(DownloadApi, "/jobs/<string:job_id>/download")
    api.add_resource(DownloadFileApi, "/download/<string:job_id>/<string:file_name>")
