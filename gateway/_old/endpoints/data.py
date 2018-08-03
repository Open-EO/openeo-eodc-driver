""" Data Discovery '/data' """

from flask.views import MethodView
from .. import gateway as gw


class ProductApi(MethodView):
    decorators = [
        gw.get_decorator("validate"),
        gw.get_decorator("auth")
    ]

    def get(self, user_id:str=None, data_id:str=None):
        arguments = {"qtype": "products", "qname": data_id}
        return gw.send_rpc("get_records", user_id, arguments)
        
        










        

# class ProductDetailApi
    
    # def post(self, user_id, body_1, body_2=None):
    #     return gw.res.data(200, body_1)











# from flask_apispec.views import MethodResource
# from flask_apispec import doc, use_kwargs
# from flask_restful.utils import cors
# from marshmallow import fields, Schema, validate

# from . import gateway
# from .src.auth import auth


# # class ProductDetailSchema(Schema):
# #     data_id = fields.Str(required=True)
# #     # qgeom = fields.Str()
# #     # qstartdate = fields.Str()
# #     # qenddate = fields.Str()


# # class ProductAPI(MethodResource):

# #     # TODO: Exclude Aliases?
# #     @cors.crossdomain(["*"], ["GET"],["Authorization", "Content-Type"], credentials=True)
# #     @auth()
# #     @doc(**gateway.spec.get_spec("/data", "get"))
# #     def get(self, user_id):
# #         try:
# #             rpc_response = gateway.rpc.data.get_records(
# #                 qtype="products")

# #             if rpc_response["status"] == "error":
# #                 raise gateway.res.map_exceptions(rpc_response, user_id)

# #             return gateway.res.data(200, rpc_response["data"])
# #         except Exception as exc:
# #             return gateway.res.error(exc)


# # class ProductDetailAPI(MethodResource):

# #     # TODO: Asked Matthias why data_id is body and url parameter?
# #     @use_kwargs(RecordRequestSchema)
# #     @cors.crossdomain(["*"], ["GET"],["Authorization", "Content-Type"], credentials=True)
# #     @auth()
# #     @doc(**gateway.spec.get_spec("/data/{data_id}", "get"))
# #     def get(self, user_id, **kwargs):
# #         try:
# #             for a in kwargs:
# #                 stop = 1
            
# #             rpc_response = gateway.rpc.data.get_records(
# #                 qtype="product_details",
# #                 qname=data_id)

# #             if rpc_response["status"] == "error":
# #                 raise gateway.res.map_exceptions(rpc_response, user_id)

# #             return gateway.res.data(200, rpc_response["data"])
# #         except Exception as exc:
# #             return gateway.res.error(exc)

# class RecordRequestSchema(Schema):
#     type = fields.Str(required=True)
#     data_id = fields.Str(required=True)
#     bbox = fields.Str(required=True)
#     start = fields.Str(required=True)
#     end = fields.Str(required=True)

# class RecordsAPI(MethodResource):

#     @use_kwargs({
#         'type': fields.Str(description="The detail level (full, short, file_paths).", required=True, validate=validate.Regexp(r"^(full|short|file_path)$")),
#         'data_id': fields.Str(description="String expression to search available datasets by name."),
#         'bbox': fields.Str(description="WKT polygon or bbox to search for available datasets that spatially intersect with the polygon."),
#         'start': fields.Str(description="ISO 8601 date/time string to find datasets with any data acquired after the given date/time."),
#         'end': fields.Str(description="ISO 8601 date/time string to find datasets with any data acquired before the given date/time."),
#     },locations=['query'])
#     @cors.crossdomain(["*"], ["GET"],["Authorization", "Content-Type"], credentials=True)
#     @auth()
#     @doc(**gateway.spec.get_spec("/records", "get"))
#     def get(self, user_id, **kwargs):
#         try:
#             rpc_response = gateway.rpc.data.get_records(
#                 qtype=kwargs["type"],
#                 qname=kwargs["data_id"] if "data_id" in kwargs else None,
#                 qgeom=kwargs["bbox"] if "bbox" in kwargs else None, 
#                 qstartdate=kwargs["start"] if "start" in kwargs else None, 
#                 qenddate=kwargs["end"] if "end" in kwargs else None)

#             if rpc_response["status"] == "error":
#                 raise gateway.res.map_exceptions(rpc_response, user_id)

#             return gateway.res.data(200, rpc_response["data"])
#         except Exception as exc:
#             return gateway.res.error(exc)



# # "products": self.get_products,
# # "product_details": self.get_product_details,  
# # "full": self.get_records_full, 
# # "short": self.get_records_shorts, 
# # "file_paths": self.get_file_paths
# # ''' /data '''

# # from flask_restful_swagger_2 import Resource, swagger
# # from flask_restful.reqparse import RequestParser
# # from flask_restful.utils import cors

# # from . import rpc

# # from .src.response import *
# # from .src.request import ModelRequestParser
# # from .src.cors import CORS
# # from .src.parameters import qtype, qname, qgeom, qstartdate, qenddate, product_id


# # class RecordsApi(Resource):
# #     __res_parser = ResponseParser()
# #     __req_parser = ModelRequestParser([qtype, qname, qgeom, qstartdate, qenddate], location="args")

# #     @cors.crossdomain(["*"], ["GET"],["Authorization", "Content-Type"], credentials=True)
# #     @auth()
# #     @doc(**gateway.spec_parser.get_spec("openeo", "/data", "get"))
# #     def get(self, user_id):
# #         try:
# #             args = self.__req_parser.parse_args()
# #             rpc_response = rpc.data.get_records(
# #                 args["qtype"],
# #                 args["qname"],
# #                 args["qgeom"],
# #                 args["qstartdate"],
# #                 args["qenddate"])

# #             if rpc_response["status"] == "error":
# #                 raise self.__res_parser.map_exceptions(rpc_response, user_id)

# #             return self.__res_parser.data(200, rpc_response["data"])
# #         except Exception as exc:
# #             return self.__res_parser.error(exc)


# # class ProductDetailApi(Resource):
# #     __res_parser = ResponseParser()

# #     @cors.crossdomain(
# #         origin=["*"],
# #         methods=["GET"],
# #         headers=["Authorization", "Content-Type"],
# #         credentials=True)
# #     @swagger.doc(CORS().__parse__([product_id]))
# #     def options(self):
# #         return self.__res_parser.code(200)

# #     @cors.crossdomain(
# #         origin=["*"],
# #         methods=["GET"],
# #         headers=["Authorization", "Content-Type"],
# #         credentials=True)
# #     @auth()
# #     @swagger.doc({
# #         "tags": ["EO Data Discovery"],
# #         "description": "Returns basic information about EO datasets that are available at the back-end.",
# #         "parameters": [product_id],
# #         "security": [{"Bearer": []}],
# #         "responses": {
# #             "200": OK("Returns further information on a given EO product available at the back-end.").__parse__(),
# #             "400": BadRequest().__parse__(),
# #             "401": Unauthorized().__parse__(),
# #             "403": Forbidden().__parse__(),
# #             "500": InternalServerError().__parse__(),
# #             "501": NotImplemented().__parse__(),
# #             "503": ServiceUnavailable().__parse__()
# #         }
# #     })
# #     def get(self, user_id, product_id):
# #         try:
# #             rpc_response = rpc.data.get_records(
# #                 qtype="product_details",
# #                 qname=product_id)

# #             if rpc_response["status"] == "error":
# #                 raise self.__res_parser.map_exceptions(rpc_response, user_id)

# #             return self.__res_parser.data(200, rpc_response["data"])
# #         except Exception as exc:
# #             return self.__res_parser.error(exc)
