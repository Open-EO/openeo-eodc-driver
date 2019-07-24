""" Gateway """

from sys import exit
from os import environ
from flask import Flask, g
from flask.ctx import AppContext
from flask.wrappers import Response
from flask_cors import CORS
from flask_nameko import FlaskPooledClusterRpcProxy
#from flask_oidc import OpenIDConnect
from typing import Union, Callable

from .dependencies import ResponseParser, OpenAPISpecParser, AuthenticationHandler, APIException, OpenAPISpecException


class Gateway:
    """Gateway is the central class to instantiate a RPC based API gateway object based on
    an OpenAPI v3 specification.
    """

    def __init__(self):
        self._service = self._init_service()
        self._rpc = self._init_rpc()
        self._res = self._init_response()
        self._spec = self._init_specs()
        self._auth = self._init_auth()

        # Decorators
        self._validate = self._spec.validate
        #self._authenticate = self._auth.oidc
        self._authenticate = self._auth.oidc_token
        self._authorize = self._auth.check_role

        # Add custom error handler
        self._service.register_error_handler(404, self._parse_error_to_json)
        self._service.register_error_handler(405, self._parse_error_to_json)

    def get_service(self) -> Flask:
        """Returns the Flask service object

        Returns:
            Flask -- The Flask object
        """
        return self._service

    def get_rpc_context(self) -> Union[AppContext, FlaskPooledClusterRpcProxy]:
        """Returns the application context of the Flask application object and the
        RPC proxy object to create new endpoints.

        Returns:
            Union[AppContext, FlaskPooledClusterRpcProxy] -- The app context and RPC proxy
        """

        ctx = self._service.app_context()
        ctx.push()

        return ctx, self._rpc

    def set_cors(self, resources: dict = {r"/*": {"origins": "*"}}):
        """Initializes the CORS header. The header rules/resources are passed using a dictonary.
        FOr more information visit: https://flask-cors.readthedocs.io/en/latest/

        Arguments:
            resources {dict} -- The resource description (default: {{r"/*": {"origins": "*"}}})
        """

        CORS(self._service, resources=resources)

    def add_endpoint(self, route: str, func: Callable, methods: list=["GET"], auth: bool=False,
        role: str=None, validate: bool=False, rpc: bool=True, is_async: bool=False):
        """Adds an endpoint to the API, pointing to a Remote Procedure Call (RPC) of a microservice or a
        local function. Serval decorators can be added to enable authentication, authorization and input
        validation.

        Arguments:
            route {str} -- The endpoint route (e.g. '/')
            func {Callable} -- The RPC or function, to which the route is pointing.

        Keyword Arguments:
            methods {list} -- The allowed HTTP methods (default: {["GET"]})
            auth {bool} -- Activate authentication (default: {False})
            admin {bool} -- Activate authorization (default: {False})
            validate {bool} -- Activate input validation (default: {False})
            rpc {bool} -- Setting up a RPC or local function (default: {True})
            is_async {bool} -- Flags if the function should be executed asynchronously (default: {False})
        """

        methods = [method.upper() for method in methods]

        if rpc: func = self._rpc_wrapper(func, is_async)
        if validate: func = self._validate(func)
        if role: func = self._authorize(func, role)
        if auth: func = self._authenticate(func)

        self._service.add_url_rule(
            route,
            view_func=func,
            endpoint=route + '_'.join(methods),
            provide_automatic_options=True,
            methods=methods)

    def validate_api_setup(self):
        """Validates the setup of the API with respect to the specification in the
        OpenAPI document. Throws an OpenAPISpecException if the validation fails.
        """
        try:
            self._spec.validate_api(self._service.url_map)
        except OpenAPISpecException as exp:
            print(" -> API setup is not valid: " + str(exp))
            exit(1)

    def _init_service(self) -> Flask:
        """Initalizes the Flask application

        Returns:
            Flask -- The instantiated Flask object
        """

        service = Flask(__name__)
        service.config.from_object(environ.get("GATEWAY_SETTINGS"))

        return service

    def _init_rpc(self) -> FlaskPooledClusterRpcProxy:
        """Initalizes the RPC proxy

        Returns:
            FlaskPooledClusterRpcProxy -- The instantiated FlaskPooledClusterRpcProxy object
        """

        self._service.config.update({
            "NAMEKO_AMQP_URI":
            "pyamqp://{0}:{1}@{2}:{3}".format(
                environ.get("RABBIT_USER"),
                environ.get("RABBIT_PASSWORD"),
                environ.get("RABBIT_HOST"),
                environ.get("RABBIT_PORT")
            ),
            "NAMEKO_serializer": "pickle",
        })

        rpc = FlaskPooledClusterRpcProxy()
        rpc.init_app(self._service)
        return rpc

    def _init_response(self) -> ResponseParser:
        """Initalizes the ResponseParser

        Returns:
            ResponseParser -- The instantiated ResponseParser object
        """

        return ResponseParser(self._service.logger)

    def _init_specs(self) -> OpenAPISpecParser:
        """Initalizes the OpenAPISpecParser

        Returns:
            OpenAPISpecParser -- The instantiated OpenAPISpecParser object
        """

        return OpenAPISpecParser(self._res)

    def _init_auth(self) -> AuthenticationHandler:
        """Initalizes the AuthenticationHandler

        Returns:
            AuthenticationHandler -- The instantiated AuthenticationHandler object
        """

        oidc_config = {
            "SECRET_KEY": environ.get("SECRET_KEY"),
            "OIDC_CLIENT_SECRETS": environ.get("OIDC_CLIENT_SECRETS"),
            "OIDC_OPENID_REALM": environ.get("OIDC_OPENID_REALM"),
            'OIDC_ID_TOKEN_COOKIE_SECURE': environ.get("OIDC_ID_TOKEN_COOKIE_SECURE") == "true"
        }
        self._service.config.update(oidc_config)

        # oicd = OpenIDConnect()
        # oicd.init_app(self._service)

        return AuthenticationHandler(self._res) #, self._rpc) #, oicd)

    def _rpc_wrapper(self, f:Callable, is_async) -> Union[Callable, Response]:
        """The RPC decorator function to handle repsonsed and exception when communicating
        with the services. This method is a single aggregated endpoint to handle the service
        communications.

        Arguments:
            f {Callable} -- The wrapped function
            is_async {bool} -- Flags if the function should be executed asynchronously

        Returns:
            Union[Callable, Response] -- Returns the decorator function or a HTTP error
        """

        def decorator(**arguments):
            try:
                rpc_response = f.call_async(**arguments) if is_async else f(**arguments)

                if is_async:
                    return self._res.parse({"code": 202}) # Fixed, since this currently just applies to POST /jobs/{job_id}/results

                if rpc_response["status"] == "error":
                    return self._res.error(rpc_response)

                return self._res.parse(rpc_response)
            except Exception as exc:
                return self._res.error(exc)
        return decorator


    def send_index(self) -> Response:
        """The function returns a JSON object containing the available routes and
        HTTP methods as defined in the OpenAPI specification.

        Returns:
            Response -- JSON object contains the API capabilities
        """
        # TODO: Index endpoint should be own rpc endpoint to be more generic
        # TODO: Implement billing plans

        api_spec = self._spec.get()

        endpoints = []
        for path_name, methods in api_spec["paths"].items():
            endpoint = {"path": path_name, "methods": []}
            for method_name, _ in methods.items():
                if method_name in ("get", "post", "patch", "put", "delete"):
                    endpoint["methods"].append(method_name.upper())
            endpoints.append(endpoint)

        capabilities = {
            "api_version": api_spec["info"]["version"],
            "backend_version": "x.x.x", # TODO include backend version
            "title": api_spec["info"]["title"],
            "description": api_spec["info"]["description"],
            "endpoints": endpoints
        }

        return self._res.parse({"code": 200, "data": capabilities})


    def send_health_check(self) -> Response:
        """Returns the the sanity check

        Returns:
            Response -- 200 HTTP code
        """

        return self._res.parse({"code": 200})


    def send_openid_connect_discovery(self) -> Response:
        """Redirects to the OpenID Connect discovery document.

        Returns:
            Response -- Redirect to the OpenID Connect discovery document
        """

        return self._res.redirect(environ.get("OPENID_DISCOVERY"))


    def send_openapi(self) -> Response:
        """Returns the parsed OpenAPI specification as JSON

        Returns:
            Response -- JSON object containing the OpenAPI specification
        """

        return self._res.parse({"code": 200, "data": self._spec.get()})


    def send_redoc(self) -> Response:
        """Returns the ReDoc clients

        Returns:
            Response -- The HTML file containing the ReDoc client setup
        """

        return self._res.parse({"html": "redoc.html"})


    def _parse_error_to_json(self, exc):
        return self._res.error(
            APIException(
                msg=str(exc),
                code=exc.code,
                service="gateway",
                internal=False))


    def get_user_info(self) -> Response:
        """Returns info about the (logged in) user.

        Returns:
            Response -- 200 HTTP code
        """

        user_info = self._auth.user_info()

        return self._res.parse({"code": 200, "data": user_info})

