""" Sanity Check '/health' """

from flask_apispec.views import MethodResource
from flask_apispec import doc
from flask_restful.utils import cors

from . import gateway
from .src.response import *

class HealthApi(MethodResource):

    __res_parser = ResponseParser()

    @cors.crossdomain(["*"], ["GET"], ["Content-Type"])
    @doc(
        tags=["Health"],
        summary="Health Check of the API gateway.",
        description="""Endpoint to test if the API gateway is up and running.""",
        responses={
            "200": OK("The gateway is running.").__parse__(),
            "503": ServiceUnavailable().__parse__()
        }
    )
    def get(self):
        return self.__res_parser.code(200)





# from flask_restful_swagger_2 import swagger, Resource
# from flask_restful.utils import cors

# from .src.response import *
# from .src.cors import CORS


# class HealthApi(Resource):
#     __res_parser = ResponseParser()

#     @cors.crossdomain(
#         origin=["*"], 
#         methods=["GET"],
#         headers=["Content-Type"])
#     @swagger.doc(CORS().__parse__())
#     def options(self):
#         return self.__res_parser.code(200)

#     @cors.crossdomain(
#         origin=["*"], 
#         methods=["GET"],
#         headers=["Content-Type"])
#     @swagger.doc({
#         "tags": ["Health"],
#         "description": "Health Check of API gateway",
#         "responses": {
#             "200": OK("The gateway is running.").__parse__(),
#             "503": ServiceUnavailable().__parse__()
#         }
#     })
#     def get(self):
#         return self.__res_parser.code(200)

# TODO: Better way -> To much overload by HTTP servers, RPC response timeout to high
# class ServiceHealthApi(Resource):
#     __res_parser = ResponseParser()

#     @cors.crossdomain(
#         origin=["*"], 
#         methods=["GET"],
#         headers=["Content-Type"])
#     @swagger.doc(CORS().__parse__())
#     def options(self):
#         return self.__res_parser.code(200)

#     @cors.crossdomain(
#         origin=["*"], 
#         methods=["GET"],
#         headers=["Content-Type"])
#     @swagger.doc({
#         "tags": ["Health"],
#         "description": "Health Check of Services",
#         "responses": {
#             "200": OK("Returns the services that are running.").__parse__(),
#             "503": ServiceUnavailable().__parse__()
#         }
#     })
#     def get(self):
#         checks = {
#             "gateway": "Running",
#             "users": "Running",
#             "data": "Running",
#             "processes": "Running",
#             "jobs": "Running"
#         }

#         try: 
#             get("http://openeo-users:8000/health", timeout=2)
#         except Exception:
#             checks["users"] = "Not Running"
        
#         try: 
#             get("http://openeo-data:8000/health", timeout=2)
#         except Exception:
#             checks["data"] = "Not Running"
        
#         try: 
#             get("http://openeo-processes:8000/health", timeout=2)
#         except Exception:
#             checks["processes"] = "Not Running"
        
#         try: 
#             get("http://openeo-jobs:8000/health", timeout=2)
#         except Exception:
#             checks["jobs"] = "Not Running"

#         return self.__res_parser.data(200, checks)