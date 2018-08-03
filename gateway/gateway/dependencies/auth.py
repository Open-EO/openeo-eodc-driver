""" AuthenticationHandler """

from flask import request
from flask.wrappers import Request, Response
from typing import Callable, Union
from flask_nameko import FlaskPooledClusterRpcProxy
from .response import ResponseParser, APIException


class AuthenticationHandler:
    """The AuthenticationHandler connects to the user service and verifies if the bearer token
    send by the user is valid.
    """

    def __init__(self, response_handler: ResponseParser, rpc_proxy: FlaskPooledClusterRpcProxy):
        self._res = response_handler
        self._rpc = rpc_proxy

    def _parse_auth_header(self, req: Request) -> Union[str, Exception]:
        """Parses and returns the bearer token. Raises an AuthenticationException if the Authorization
        header in the request is not correct.
        
        Arguments:
            req {Request} -- The Request object
        
        Returns:
            Union[str, Exception] -- Returns the bearer token as string or raises an exception
        """

        if "Authorization" not in req.headers or not req.headers["Authorization"]:
            raise APIException(
                msg="Missing 'Authorization' header.",
                code=400,
                servide="gateway",
                internal=False)

        token_split = req.headers["Authorization"].split(" ")

        if len(token_split) != 2 or token_split[0] != "Bearer":
            raise APIException(
                msg="Invalid Bearer token.",
                code=401,
                servide="gateway",
                internal=False)

        return token_split[1]

    def bearer(self, f: Callable) -> Union[Callable, Response]:
        """Decorator function to authenticate the user, using a bearer token
        that is contained within the response header. Returns a HTTP error if the
        bearer token is not valid.
        
        Arguments:
            f {Callable} -- The wrapped function
        
        Returns:
            Union[Callable, Response] -- Returns the decorator function or a HTTP error 
        """
        # TODO: Decorator for authorization -> or (admin and not user["admin"])

        def decorator(*args, **kwargs):
            try:
                token = self._parse_auth_header(request)
                rpc_response = self._rpc.auth.identify(token)

                if rpc_response["status"] == "error":
                    raise self._res.error(rpc_response)

                user = rpc_response["data"]

                if not user["active"]:  
                    raise APIException(
                        msg="User is not active.",
                        code=403,
                        servide="gateway",
                        internal=False)

                return f(user_id=user["user_id"])
            except Exception as exc:
                return self._res.error(exc)
        return decorator
