''' /processes '''

from flask_restful_swagger_2 import Resource, swagger
from flask_restful.reqparse import RequestParser
from flask_restful.utils import cors
from flask import request

from . import rpc
from .src.auth import auth
from .src.response import *
from .src.request import ModelRequestParser
from .src.cors import CORS
from .src.parameters import process_body, process_id, qname
from .src.models import process_description


class ProcessApi(Resource):
    __res_parser = ResponseParser()
    __req_parser = ModelRequestParser(process_description)
    __req_q_parser = ModelRequestParser([qname], location="args")

    @cors.crossdomain(
        origin=["*"],
        methods=["GET", "POST"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    @swagger.doc(CORS().__parse__())
    def options(self):
        return self.__res_parser.code(200)

    @cors.crossdomain(
        origin=["*"],
        methods=["GET", "POST"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    @auth(admin=True)
    @swagger.doc({
        "tags": ["Process Discovery"],
        "description": "Registers a new process.",
        "parameters": [process_body],
        "security": [{"Bearer": []}],
        "responses": {
            "200": OK("Details of the created process.").__parse__(),
            "400": BadRequest().__parse__(),
            "401": Unauthorized().__parse__(),
            "403": Forbidden().__parse__(),
            "500": InternalServerError().__parse__(),
            "501": NotImplemented().__parse__(),
            "503": ServiceUnavailable().__parse__()
        }
    })
    def post(self, user_id):
        try:
            args = self.__req_parser.parse_args()
            rpc_response = rpc.processes.create_process(user_id, args)

            if rpc_response["status"] == "error":
                raise self.__res_parser.map_exceptions(rpc_response, user_id)

            return self.__res_parser.data(200, rpc_response["data"])
        except Exception as exc:
            return self.__res_parser.error(exc)

    @cors.crossdomain(
        origin=["*"], 
        methods=["GET", "POST"], 
        headers=["Authorization", "Content-Type"], 
        credentials=True)
    @auth()
    @swagger.doc({
        "tags": ["Process Discovery"],
        "description": "Returns processes supported by the back-end.",
        "parameters": [qname],
        "security": [{"Bearer": []}],
        "responses": {
            "200": OK("An array of EO processes including their unique identifiers and a description.").__parse__(),
            "401": Unauthorized().__parse__(),
            "403": Forbidden().__parse__(),
            "500": InternalServerError().__parse__(),
            "501": NotImplemented().__parse__(),
            "503": ServiceUnavailable().__parse__()
        }
    })
    def get(self, user_id):
        try:
            args = self.__req_q_parser.parse_args()
            rpc_response = rpc.processes.get_all_processes(args["qname"])

            if rpc_response["status"] == "error":
                raise self.__res_parser.map_exceptions(rpc_response, user_id)

            return self.__res_parser.data(200, rpc_response["data"])
        except Exception as exc:
            return self.__res_parser.error(exc)


class ProcessDetailApi(Resource):
    __res_parser = ResponseParser()

    @cors.crossdomain(
        origin=["*"],
        methods=["GET"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    @swagger.doc(CORS().__parse__([process_id]))
    def options(self):
        return self.__res_parser.code(200)

    @cors.crossdomain(
        origin=["*"], 
        methods=["GET"], 
        headers=["Authorization", "Content-Type"], 
        credentials=True)
    @auth()
    @swagger.doc({
        "tags": ["Process Discovery"],
        "description": "Returns further information on a given EO process available at the back-end.",
        "parameters": [process_id],
        "security": [{"Bearer": []}],
        "responses": {
            "200": OK("JSON object with metadata of the EO process.").__parse__(),
            "401": Unauthorized().__parse__(),
            "403": Forbidden().__parse__(),
            "404": NotFound().__parse__(),
            "500": InternalServerError().__parse__(),
            "501": NotImplemented().__parse__(),
            "503": ServiceUnavailable().__parse__()
        }
    })
    def get(self, user_id, process_id):
        try:
            rpc_response = rpc.processes.get_process(process_id)

            if rpc_response["status"] == "error":
                raise self.__res_parser.map_exceptions(rpc_response, user_id)

            return self.__res_parser.data(200, rpc_response["data"])
        except Exception as exc:
            return self.__res_parser.error(exc)
