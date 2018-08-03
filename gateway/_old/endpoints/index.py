""" Index '/' """

from flask.views import MethodView
from .. import gateway as gw

class Index(MethodView):
    def get(self, user_id:str=1, path_1:int=2, path_2:str=None):
        api_spec = gw.spec.to_dict() 

        endpoints = []
        for path_name, methods in api_spec["paths"].items():
            endpoint = {"path": path_name, "methods": []}
            for method_name, _ in methods.items():
                if method_name in ("get", "post", "patch", "put", "delete"):
                    endpoint["methods"].append(method_name.upper())
            endpoints.append(endpoint)

        # TODO: Implement billing plans
        capabilities = { 
            "version": api_spec["info"]["version"],
            "endpoints": endpoints
        }

        return gw.res.data(200, capabilities)
