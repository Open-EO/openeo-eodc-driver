""" Gateway """

from os import environ
from sys import exit
from typing import Union, Callable

from flask import Flask, redirect, url_for
from flask.ctx import AppContext
from flask.wrappers import Response
from flask_cors import CORS
from flask_nameko import FlaskPooledClusterRpcProxy
from flask_sqlalchemy import SQLAlchemy

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
        self._user_db = self._init_users_db()

        # Decorators
        self._validate = self._spec.validate
        self._validate_custom = self._spec.validate_custom
        self._authenticate = self._auth.validate_token

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

    def get_user_db(self):
        return self._user_db

    def set_cors(self, resources: dict = {r"/*": {"origins": "*"}}):
        """Initializes the CORS header. The header rules/resources are passed using a dictonary.
        FOr more information visit: https://flask-cors.readthedocs.io/en/latest/

        Arguments:
            resources {dict} -- The resource description (default: {{r"/*": {"origins": "*"}}})
        """

        CORS(self._service, resources=resources, vary_header=False, supports_credentials=True)

    def add_endpoint(self, route: str, func: Callable, methods: list = None, auth: bool = False,
                     role: str = 'user', validate: bool = False, validate_custom: bool = False, rpc: bool = True,
                     is_async: bool = False, parse_spec: bool = False):
        """Adds an endpoint to the API, pointing to a Remote Procedure Call (RPC) of a microservice or a
        local function. Serval decorators can be added to enable authentication, authorization and input
        validation.

        Arguments:
            route {str} -- The endpoint route (e.g. '/')
            func {Callable} -- The RPC or function, to which the route is pointing.

        Keyword Arguments:
            methods {list} -- The allowed HTTP methods (default: {["GET"]})
            auth {bool} -- Activate authentication (default: {False})
            role {str} -- User role, e.g.: admin (default: {user})
            validate {bool} -- Activate input validation (default: {False})
            validate_custom {bool} -- Activate custom input validation, enable parameter parsing (default: {False})
            rpc {bool} -- Setting up a RPC or local function (default: {True})
            is_async {bool} -- Flags if the function should be executed asynchronously (default: {False})
            parse_spec {bool} -- Flag if the function should get the openapi specs (default: {False})
        """

        if not methods:
            methods = ["GET"]
        # Method OPTIONS needed for CORS
        if "OPTIONS" not in methods:
            methods.append("OPTIONS")
        methods = [method.upper() for method in methods]

        if parse_spec:
            api_spec = self._spec.get()
            func = self._rpc_wrapper(func, is_async, api_spec=api_spec) if rpc else self._local_wrapper(func, api_spec=api_spec)
        else:
            # Use either rpc or local wrapper to handle responses and exceptions
            func = self._rpc_wrapper(func, is_async) if rpc else self._local_wrapper(func)
        if validate:
            func = self._validate(func)
        elif validate_custom:
            func = self._validate_custom(func)
        if auth:
            func = self._authenticate(func, role)

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

        return AuthenticationHandler(self._res)

    def _init_users_db(self) -> SQLAlchemy:
        db_url = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
            environ.get("DB_USER"),
            environ.get("DB_PASSWORD"),
            environ.get("DB_HOST"),
            environ.get("DB_PORT"),
            environ.get("DB_NAME")
        )
        self._service.config.update({
            "SQLALCHEMY_DATABASE_URI": db_url,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        })
        return SQLAlchemy(self._service)

    def _rpc_wrapper(self, f: Callable, is_async, **kwargs) -> Union[Callable, Response]:
        """The RPC decorator function handles responses and exception when communicating
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
                rpc_response = f.call_async(**arguments, **kwargs) if is_async else f(**arguments, **kwargs)

                if is_async:
                    return self._res.parse({"code": 202}) # Fixed, since this currently just applies to POST /jobs/{job_id}/results

                if rpc_response["status"] == "error":
                    return self._res.error(rpc_response)

                return self._res.parse(rpc_response)
            except Exception as exc:
                return self._res.error(exc)
        return decorator

    def _local_wrapper(self, f: Callable, **kwargs) -> Union[Callable, Response]:
        """The local decorator function handles responses and exception for non-RPC functions.

        Arguments:
            f {Callable} -- The wrapped function

        Returns:
            Union[Callable, Response] -- Returns the decorator function or a HTTP error
        """
        def local_decorator(**arguments):
            try:
                local_response = f(**arguments, **kwargs)
                if local_response.status_code == 302:
                    # This is a redirect, pass repsonse as it is
                    # currently used only to redirect "/" to ".well-known/openeo" 
                    return local_response

                if local_response["status"] == "error":
                    return self._res.error(local_response)
                elif local_response["status"] == "redirect":
                    return self._res.redirect(local_response["url"])
                return self._res.parse(local_response)

            except Exception as exc:
                return self._res.error(exc)

        return local_decorator

    def send_health_check(self) -> dict:
        """Returns the the sanity check

        Returns:
            Dict -- 200 HTTP code
        """

        return {
            "status": "success",
            "code": 200,
        }

    def send_openapi(self) -> dict:
        """Returns the parsed OpenAPI specification as JSON

        Returns:
            Dict -- JSON object containing the OpenAPI specification
        """

        return {
            "status": "success",
            "code": 200,
            "data": self._spec.get(),
        }

    def send_redoc(self) -> dict:
        """Returns the ReDoc clients

        Returns:
            Dict -- The HTML file containing the ReDoc client setup
        """

        return {
            "status": "success",
            "html": "redoc.html",
        }
    
    
    def main_page(self) -> dict:
        """
        Redirect main page "/" to openeo well known dodument "/.well-known/openeo".
        """
        
        if environ['DEVELOPMENT']:
            base_url = environ['GATEWAY_URL']
        else:
            base_url = environ['DNS_URL']
        return redirect(base_url + "/.well-known/openeo")
        

    def _parse_error_to_json(self, exc):
        return self._res.error(
            APIException(
                msg=str(exc),
                code=exc.code,
                service="gateway",
                internal=False))
