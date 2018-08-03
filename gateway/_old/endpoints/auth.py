""" Authentication '/credentials' '/me' """

from flask import request
from flask.views import MethodView

from .. import gateway as gw


class AuthBasicAPI(MethodView):

    # @cors.crossdomain(["*"], ["GET"], ["Authorization", "Content-Type"], credentials=True)
    # @doc(**gateway.spec.get_spec("/credentials/basic", "get"))
    def get(self):
        try:
            if not request.authorization:
                exp = {"status": "error", "service": "auth", "key": "Unauthorized", "msg": "Basic Auth header is missing"}
                raise gw.res.map_exceptions(exp, None)

            rpc_response = gw.rpc.auth.login(
                request.authorization["username"],
                request.authorization["password"])

            if rpc_response["status"] == "error":
                raise gw.res.map_exceptions(rpc_response, None)

            return gw.res.data(200, rpc_response["data"])
        except Exception as exc:
            return gw.res.error(exc)


# from flask import request
# from flask_restful_swagger_2 import Resource, swagger
# from flask_restful.reqparse import RequestParser
# from flask_restful.utils import cors

# from . import rpc
# from .src.response import *
# from .src.request import ModelRequestParser
# from .src.parameters import password_body
# from .src.models import password
# from .src.cors import CORS


# class AuthBasicAPI(Resource):
#     @cors.crossdomain(["*"], ["GET"], ["Authorization", "Content-Type"], credentials=True)
#     @doc(**gateway.spec.get_spec("openeo", "/credentials/basic", "get"))
#     @swagger.doc({
#         "tags": ["Authentication"],
#         "description": "Check whether the user is registered with the specified credentials at the back-end.",
#         "security": [{"Basic": []}],
#         "responses": {
#             "200": OK("Login successful. Returns the user ID and a bearer token for future API calls.").__parse__(),
#             "401": Unauthorized().__parse__(),
#             "403": Forbidden().__parse__(),
#             "500": InternalServerError().__parse__(),
#             "501": NotImplemented().__parse__(),
#             "503": ServiceUnavailable().__parse__()
#         }
#     })
#     def get(self):
#         try:
#             if not request.authorization:
#                 exp = {"status": "error", "service": "auth", "key": "Unauthorized", "msg": "Basic Auth header is missing"}
#                 raise self.__res_parser.map_exceptions(exp, None)

#             rpc_response = rpc.auth.login(
#                 request.authorization["username"],
#                 request.authorization["password"])

#             if rpc_response["status"] == "error":
#                 raise self.__res_parser.map_exceptions(rpc_response, None)

#             return self.__res_parser.data(200, rpc_response["data"])
#         except Exception as exc:
#             return self.__res_parser.error(exc)


# class RegisterApi(Resource):
#     __res_parser = ResponseParser()
#     __req_parser = ModelRequestParser(password)

#     @cors.crossdomain(
#         origin=["*"],
#         methods=["GET"],
#         headers=["Authorization", "Content-Type"],
#         credentials=True)
#     @swagger.doc(CORS().__parse__())
#     def options(self):
#         return self.__res_parser.code(200)

#     @cors.crossdomain(
#         origin=["*"], 
#         methods=["POST"], 
#         headers=["Authorization", "Content-Type"], 
#         credentials=True)
#     @swagger.doc({
#         "tags": ["Authentication"],
#         "description": "Registers a new user account.",
#         "parameters": [password_body],
#         "responses": {
#             "200": OK("Registration successful. Returns the newly created user ID.").__parse__(),
#             "400": BadRequest().__parse__(),
#             "500": InternalServerError().__parse__(),
#             "501": NotImplemented().__parse__(),
#             "503": ServiceUnavailable().__parse__()
#         }
#     })
#     def post(self):
#         try:
#             args = self.__req_parser.parse_args()
#             rpc_response = rpc.users.create_user(args["password"])

#             if rpc_response["status"] == "error":
#                 raise self.__res_parser.map_exceptions(rpc_response, None)

#             return self.__res_parser.data(200, rpc_response["data"])
#         except Exception as exc:
#             return self.__res_parser.error(exc)
