''' /data '''

from flask_restful_swagger_2 import Resource, swagger
from flask_restful.reqparse import RequestParser
from flask_restful.utils import cors

from . import rpc
from .src.auth import auth
from .src.response import *
from .src.request import ModelRequestParser
from .src.cors import CORS
from .src.parameters import qtype, qname, qgeom, qstartdate, qenddate, product_id


class RecordsApi(Resource):
    __res_parser = ResponseParser()
    __req_parser = ModelRequestParser([qtype, qname, qgeom, qstartdate, qenddate], location="args")

    @cors.crossdomain(
        origin=["*"],
        methods=["GET"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    @swagger.doc(CORS().__parse__())
    def options(self):
        return self.__res_parser.code(200)

    @cors.crossdomain(
        origin=["*"],
        methods=["GET"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    @auth()
    @swagger.doc({
        "tags": ["EO Data Discovery"],
        "description": "Returns basic information about EO datasets that are available at the back-end.",
        "parameters": [qtype, qname, qgeom, qstartdate, qenddate],
        "security": [{"Bearer": []}],
        "responses": {
            "200": OK("An array of EO datasets including their unique identifiers and some basic metadata.").__parse__(),
            "400": BadRequest().__parse__(),
            "401": Unauthorized().__parse__(),
            "403": Forbidden().__parse__(),
            "500": InternalServerError().__parse__(),
            "501": NotImplemented().__parse__(),
            "503": ServiceUnavailable().__parse__()
        }
    })
    def get(self, user_id):
        try:
            args = self.__req_parser.parse_args()
            rpc_response = rpc.data.get_records(
                args["qtype"],
                args["qname"],
                args["qgeom"],
                args["qstartdate"],
                args["qenddate"])

            if rpc_response["status"] == "error":
                raise self.__res_parser.map_exceptions(rpc_response, user_id)

            return self.__res_parser.data(200, rpc_response["data"])
        except Exception as exc:
            return self.__res_parser.error(exc)


class ProductDetailApi(Resource):
    __res_parser = ResponseParser()

    @cors.crossdomain(
        origin=["*"],
        methods=["GET"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    @swagger.doc(CORS().__parse__([product_id]))
    def options(self):
        return self.__res_parser.code(200)

    @cors.crossdomain(
        origin=["*"],
        methods=["GET"],
        headers=["Authorization", "Content-Type"],
        credentials=True)
    @auth()
    @swagger.doc({
        "tags": ["EO Data Discovery"],
        "description": "Returns basic information about EO datasets that are available at the back-end.",
        "parameters": [product_id],
        "security": [{"Bearer": []}],
        "responses": {
            "200": OK("Returns further information on a given EO product available at the back-end.").__parse__(),
            "400": BadRequest().__parse__(),
            "401": Unauthorized().__parse__(),
            "403": Forbidden().__parse__(),
            "500": InternalServerError().__parse__(),
            "501": NotImplemented().__parse__(),
            "503": ServiceUnavailable().__parse__()
        }
    })
    def get(self, user_id, product_id):
        try:
            rpc_response = rpc.data.get_records(
                qtype="product_details",
                qname=product_id)

            if rpc_response["status"] == "error":
                raise self.__res_parser.map_exceptions(rpc_response, user_id)

            return self.__res_parser.data(200, rpc_response["data"])
        except Exception as exc:
            return self.__res_parser.error(exc)
