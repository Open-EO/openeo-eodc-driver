""" / """
from flask_restful_swagger_2 import swagger, Resource
from flask_restful.utils import cors
from requests import get

from . import rpc
from .src.response import *
from .src.cors import CORS


class SwaggerApi(Resource):
    __res_parser = ResponseParser()

    @cors.crossdomain(
        origin=["*"], 
        methods=["GET"],
        headers=["Content-Type"])
    def options(self):
        return self.__res_parser.code(200)

    @cors.crossdomain(
        origin=["*"], 
        methods=["GET"],
        headers=["Content-Type"])
    def get(self):
        return self.__res_parser.html("redoc.html")
