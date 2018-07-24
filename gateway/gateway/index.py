""" / """
from flask_restful_swagger_2 import swagger, Resource
from flask_restful.utils import cors
from requests import get

from . import rpc
from .src.response import *
from .src.cors import CORS


class Index(Resource):
    __res_parser = ResponseParser()

    @cors.crossdomain(
        origin=["*"], 
        methods=["GET"],
        headers=["Content-Type"])
    @swagger.doc(CORS().__parse__())
    def options(self):
        return self.__res_parser.code(200)

    @cors.crossdomain(
        origin=["*"], 
        methods=["GET"],
        headers=["Content-Type"])
    @swagger.doc({
        "tags": ["Capabilities"],
        "description": "Returns the capabilities, i.e., which OpenEO API features are supported by the back-end.",
        "responses": {
            "200": OK("An array of implemented API endpoints.").__parse__(),
            "503": ServiceUnavailable().__parse__()
        }
    })
    def get(self):
        capabilities = [
            "/",
            "/health",
            "/health/services",
            "/auth/register",
            "/auth/login",
            "/data/<string:product_id>",
            "/processes",
            "/processes/<string:process_id>",
            "/jobs",
            "/jobs/<string:job_id>",
            "/jobs/<string:job_id>/queue",
            "/jobs/<string:job_id>/download",
            "/download/<string:job_id>/<string:file_name>"
        ]

        return self.__res_parser.data(200, capabilities)
