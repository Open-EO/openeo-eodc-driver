""" ReDoc endpoint '/redoc' """

from flask import make_response, request
from flask.views import MethodView

from .. import gateway as gw


class Specs(MethodView):
    def get(self):
        return gw.res.data(200, gw.spec.to_dict())


class ReDoc(MethodView):
    def get(self):
        return gw.res.html("redoc.html")

# class ReDoc(MethodResource):

#     @cors.crossdomain(["*"], ["GET"], ["Content-Type"])
#     @doc(
#         tags=["ReDoc"],
#         summary="ReDoc OpenAPI reference",
#         description="Returns a client for the ReDoc reference system.",
#     )
#     def get(self):
#         return gateway.res.html("redoc.html")
