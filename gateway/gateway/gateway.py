""" Gateway """

from sys import exit
from os import environ
from flask import Flask, g
from flask.ctx import AppContext
from flask.wrappers import Response
from flask_cors import CORS
from flask_nameko import FlaskPooledClusterRpcProxy
from flask_oidc import OpenIDConnect
from typing import Union, Callable

from .dependencies import ResponseParser, OpenAPISpecParser, AuthenticationHandler, APIException, OpenAPISpecException


class Gateway:
    """Gateway is the central class to instantiate a RPC based API gateway object based on
    an OpenAPI v3 specification. The dependencies of the gateway are injected into the object.
    """

    def __init__(self):
        self._service = self._init_service()
        self._rpc = self._init_rpc()
        self._res = self._init_response()
        self._spec = self._init_specs()
        self._auth = self._init_auth()
        
        # Decorators
        self._validate = self._spec.validate
        self._authenticate = self._auth.oidc
        self._authorize = self._auth.check_role 

        # Setup system endpoints
        self._init_index()
        self._init_openid_discovery()
        self._init_openapi()
        self._init_redoc()

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

    def add_endpoint(self, route: str, func: Callable, methods: list=["GET"],
                     auth: bool=False, role: str=None, validate: bool=False, rpc: bool=True):
        """Adds an endpoint to the API, pointing to a Remote Procedure Call (RPC) of a microservice or a
        local function. Serval decorators can be added to enable authentication, authorization and input 
        validation.

        Arguments:
            route {str} -- The endpoint route (e.g. '/')
            func {Callable} -- The RPC or function, to which the route is pointing.
        
        Keyword Arguments:
            methods {list} -- The allowed HTTP methods (default: {["GET"]})
            auth {bool} -- Activate authentication (default: {False})   TODO
            admin {bool} -- Activate authorization (default: {False})   TODO
            validate {bool} -- Activate input validation (default: {False})
            rpc {bool} -- Setting up a RPC or local function (default: {True})
        """

        methods = [method.upper() for method in methods]

        if rpc: func = self._rpc_wrapper(func)
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
            )
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
            'OIDC_ID_TOKEN_COOKIE_SECURE': False    # TODO: Just for development
        }

        self._service.config.update(oidc_config)

        oicd = OpenIDConnect()
        oicd.init_app(self._service)

        return AuthenticationHandler(self._res, self._rpc, oicd)

    def _rpc_wrapper(self, f:Callable) -> Union[Callable, Response]:
        """The RPC decorator function to handle repsonsed and exception when communicating 
        with the services. This method is a single aggregated endpoint to handle the service 
        communications.
        
        Arguments:
            f {Callable} -- The wrapped function
        
        Returns:
            Union[Callable, Response] -- Returns the decorator function or a HTTP error 
        """

        def decorator(**arguments):
            try:
                rpc_response = f(**arguments)

                if rpc_response["status"] == "error":
                    return self._res.error(rpc_response)

                return self._res.parse(rpc_response)
            except Exception as exc:
                return self._res.error(exc)
        return decorator

    def _init_index(self):
        """Initializes the '/' index route and returns a endpoint function.
        """
        # TODO: Index endpoint should be own rpc endpoint to be more generic
        # TODO: Implement billing plans

        def send_index() -> Response:
            """The function returns a JSON object containing the available routes and
            HTTP methods as defined in the OpenAPI specification.
            
            Returns:
                Response -- JSON object contains the API capabilities
            """

            api_spec = self._spec.get()

            endpoints = []
            for path_name, methods in api_spec["paths"].items():
                endpoint = {"path": path_name, "methods": []}
                for method_name, _ in methods.items():
                    if method_name in ("get", "post", "patch", "put", "delete"):
                        endpoint["methods"].append(method_name.upper())
                endpoints.append(endpoint)
            
            capabilities = {
                "version": api_spec["info"]["version"],
                "endpoints": endpoints
            }

            return self._res.parse({"code": 200, "data": capabilities})

        self.add_endpoint("/", send_index, rpc=False)
    
    def _init_openid_discovery(self):
        """Initializes the '/credentials/oidc' route and returns a endpoint function.
        """

        def send_openid_connect_discovery() -> Response:
            """Redirects to the OpenID Connect discovery document.
            
            Returns:
                Response -- Redirect to the OpenID Connect discovery document
            """

            return self._res.redirect(environ.get("OPENID_DISCOVERY"))

        self.add_endpoint("/credentials/oidc", send_openid_connect_discovery, rpc=False)

    def _init_openapi(self):
        """Initializes the '/openapi' route and returns a endpoint function.
        """

        def send_openapi() -> Response:
            """Returns the parsed OpenAPI specification as JSON
            
            Returns:
                Response -- JSON object containing the OpenAPI specification
            """

            return self._res.parse({"code": 200, "data": self._spec.get()})

        self.add_endpoint("/openapi", send_openapi, rpc=False)

    def _init_redoc(self):
        """Initializes the '/redoc' route and returns a endpoint function.
        """

        def send_redoc() -> Response:
            """Returns the ReDoc clients
            
            Returns:
                Response -- The HTML file containing the ReDoc client setup
            """

            return self._res.parse({"html": "redoc.html"})

        self.add_endpoint("/redoc", send_redoc, rpc=False)
    
    def _parse_error_to_json(self, exc):
        return self._res.error(
            APIException(
                msg=str(exc),
                code=exc.code,
                service="gateway",
                internal=False))