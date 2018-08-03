from flask.views import MethodView
from .. import gateway as gw


class TestApi(MethodView):
    decorators = [
        gw.get_decorator("validate"),
        gw.get_decorator("auth")
    ]

    def get(self, user_id:str=1, path_1:int=2, path_2:str=None):
        return gw.res.data(200, path_1)
    
    def post(self, user_id, body_1, body_2=None):
        return gw.res.data(200, body_1)
