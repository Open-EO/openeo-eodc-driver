""" AuthenticationHandler """

from os import environ
from flask import request, g
from flask.wrappers import Request, Response
from flask_oidc import OpenIDConnect
from flask_nameko import FlaskPooledClusterRpcProxy
from requests import post, exceptions
from jwt import decode
from typing import Callable, Union

from .response import ResponseParser, APIException


class AuthenticationHandler:
    """The AuthenticationHandler connects to the user service and verifies if the bearer token
    send by the user is valid.
    """

    def __init__(self, response_handler: ResponseParser, rpc_proxy: FlaskPooledClusterRpcProxy, oidc: OpenIDConnect):
        self._res = response_handler
        self._rpc = rpc_proxy
        self._oidc = oidc

    def oidc(self, f):
        def decorator(*args, **kwargs):
            try:
                if g.oidc_id_token is None:
                    return self._oidc.redirect_to_auth_server(request.url)
                
                user_id = self._oidc.user_getfield("sub")

                if not self._oidc.user_getfield("email_verified"):  
                    raise APIException(
                        msg="The email address of user {0} is not verified."\
                            .format(user_id),
                        code=401,
                        service="gateway",
                        internal=False)
                    
                return f(user_id=user_id)
            except exceptions.HTTPError as exc:
                raise APIException(
                    msg=str(exc),
                    code=401,
                    service="gateway",
                    internal=False)
            except Exception as exc:
                return self._res.error(exc)
        return decorator
    
    def check_role(self, f, role):
        def decorator(user_id=None):
            try:
                token = self._parse_auth_header(request)
                roles = self._get_roles(token)
                
                if role not in roles:
                    raise APIException(
                        msg="The user {0} is not authorized to access this ressources."\
                            .format(user_id),
                        code=403,
                        service="gateway",
                        internal=False)

                return f(user_id=user_id)
            except Exception as exc:
                return self._res.error(exc)
        return decorator 

    def _get_roles(self, token):
        roles = []
        if token:
            token_decode = decode(token, algorithms=['HS256'], verify=False)
            roles = token_decode["resource_access"]["openeo"]["roles"]
        return roles

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
                service="gateway",
                internal=False)

        token_split = req.headers["Authorization"].split(" ")

        if len(token_split) != 2 or token_split[0] != "Bearer":
            raise APIException(
                msg="Invalid Bearer token.",
                code=401,
                service="gateway",
                internal=False)

        return token_split[1]


    # !!! INFO: Replaced Bearer Tokens with OIDC
    # def bearer(self, f: Callable) -> Union[Callable, Response]:
    #     """Decorator function to authenticate the user, using a bearer token
    #     that is contained within the response header. Returns a HTTP error if the
    #     bearer token is not valid.
        
    #     Arguments:
    #         f {Callable} -- The wrapped function
        
    #     Returns:
    #         Union[Callable, Response] -- Returns the decorator function or a HTTP error 
    #     """
    #     # TODO: Decorator for authorization -> or (admin and not user["admin"])

    #     def decorator(*args, **kwargs):
    #         try:
    #             rpc_response = self._rpc.auth.identify(token)

    #             if rpc_response["status"] == "error":
    #                 raise self._res.error(rpc_response)

    #             user = rpc_response["data"]

    #             if not user["active"]:  
    #                 raise APIException(
    #                     msg="User is not active.",
    #                     code=response.status_code,
    #                     servide="gateway",
    #                     internal=False)

    #             return f(user_id=user["user_id"])
    #         except exceptions.HTTPError as exc:
    #             raise APIException(
    #                 msg=str(exc),
    #                 code=response.status_code,
    #                 service="gateway",
    #                 internal=False)
    #         except Exception as exc:
    #             return self._res.error(exc)
    #     return decorator
