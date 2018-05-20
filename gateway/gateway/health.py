""" /health """
from flask_restful_swagger_2 import swagger, Resource
from flask_restful.utils import cors
from nameko.exceptions import RpcTimeout
from eventlet import Timeout

from . import rpc
from .src.response import *
from .src.cors import CORS

class HealthApi(Resource):
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
        "tags": ["Health"],
        "description": "Health Check of API",
        "responses": {
            "200": OK("Returns the services that are running.").__parse__(),
            "503": ServiceUnavailable().__parse__()
        }
    })
    def get(self):
        checks = {"gateway": "Running"}

        try:
            rpc.auth.health()
            checks["auth"] = "Running"
        except RpcTimeout:
            checks["auth"] = "Not Running"

        try:
            rpc.users.health()
            checks["users"] = "Running"
        except RpcTimeout:
            checks["users"] = "Not Running"

        try:
            rpc.data.health()
            checks["data"] = "Running"
        except RpcTimeout:
            checks["data"] = "Not Running"

        try:
            rpc.processes.health()
            checks["processes"] = "Running"
        except RpcTimeout:
            checks["processes"] = "Not Running"

        return self.__res_parser.data(200, checks)
