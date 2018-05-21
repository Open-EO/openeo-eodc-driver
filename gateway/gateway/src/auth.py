from functools import wraps
from flask import request
from nameko.exceptions import RpcTimeout

from .. import rpc
from .response import *

__res_parser = ResponseParser()

def get_token(req):
    if "Authorization" not in req.headers or not req.headers["Authorization"]:
        raise Unauthorized

    token_split = req.headers["Authorization"].split(" ")

    if len(token_split) != 2 or token_split[0] != "Bearer":
        raise Unauthorized

    return token_split[1]

def auth(admin=False):
    def decorator(f):
        @wraps(f)
        def decorated_function(self, *args, **kwargs):
            try:
                token = get_token(request)
                rpc_response = rpc.auth.identify(token)

                if rpc_response["status"] == "error":
                    raise __res_parser.map_exceptions(rpc_response["exc_key"])
                
                user = rpc_response["data"]

                if not user["active"] or (admin and not user["admin"]):
                    raise Unauthorized

                return f(self, user["user_id"], *args, **kwargs)
            except Exception as exc:
                return __res_parser.error(exc)
        return decorated_function
    return decorator
