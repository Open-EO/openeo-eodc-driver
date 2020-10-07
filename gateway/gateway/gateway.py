"""Manage initialisation and creation of API gateway."""

from sys import exit
from typing import Any, Callable, Tuple, Union

from dynaconf import FlaskDynaconf, settings
from flask import Flask
from flask.ctx import AppContext
from flask.wrappers import Response
from flask_cors import CORS
from flask_nameko import FlaskPooledClusterRpcProxy
from nameko.rpc import MethodProxy
from werkzeug.utils import redirect
from werkzeug.wrappers import Response as WerkzeugResponse

from .dependencies.auth import AuthRequirement as AuthReq, AuthenticationHandler
from .dependencies.response import APIException, ResponseParser
from .dependencies.specs import OpenAPISpecException, OpenAPISpecParser
from .dependencies.utils import GatewayUtils


class Gateway:
    """Gateway is the central class to to instantiate a RPC based API gateway object.

    The gateway is configured by a set of environment variables and an OpenAPI v3 specification.
    """

    utils = GatewayUtils()

    def __init__(self) -> None:
        """Initialize gateway and all required connections."""
        self._service = self._init_service()
        self._rpc = self._init_rpc()
        self._res = self._init_response()
        self._spec = self._init_specs()
        self._auth = self._init_auth()

        # Decorators
        self._validate = self._spec.validate
        self._validate_custom = self._spec.validate_custom
        self._authenticate = self._auth.authenticate

        # Add custom error handler
        self._service.register_error_handler(404, self._parse_error_to_json)
        self._service.register_error_handler(405, self._parse_error_to_json)

    def get_service(self) -> Flask:
        """Return the :class:`~flask.Flask` service object."""
        return self._service

    def get_rpc_context(self) -> Tuple[AppContext, FlaskPooledClusterRpcProxy]:
        """Return the Flask application context and the RPC proxy object.

        The latter can be used to create new endpoints.
        """
        ctx = self._service.app_context()
        ctx.push()

        return ctx, self._rpc

    def set_cors(self, resources: dict = None) -> None:
        """Initializes the CORS header.

        The header rules/resources are passed using a dictionary.
        For more information visit: https://flask-cors.readthedocs.io/en/latest/

        Args:
            resources: The resource description (default: {{r"/*": {"origins": "*"}}})
        """
        resources = resources if resources else {r"/*": {"origins": "*"}}
        CORS(self._service, resources=resources, vary_header=False, supports_credentials=True)

    def add_endpoint(self, route: str, func: Union[Callable, MethodProxy], methods: list = None,
                     auth: AuthReq = AuthReq.token_optional, role: str = 'user', validate: bool = False,
                     validate_custom: bool = False, rpc: bool = True,
                     is_async: bool = False, parse_spec: bool = False) -> None:
        """Adds an endpoint to the API.

        The endpoint can point to a Remote Procedure Call (RPC) of a microservice or a local function. Several
        decorators can be added to enable authentication, authorization and input validation.

        Args:
            route: The endpoint route (e.g. '/').
            func: The RPC or function, to which the route is pointing.
            methods: The allowed HTTP methods (default: {["GET"]}).
            auth: Activate authentication (token / password, required / optional).
            role: User role, e.g.: admin.
            validate: Activate input validation.
            validate_custom: Activate custom input validation, enable parameter parsing. Currently this does not
                validate any parameters but only parses them directly to the destination function.
            rpc: Setting up a RPC or local function.
            is_async: Flags if the function should be executed asynchronously.
            parse_spec: Flag if the function should get the openapi specs as a parameter.
        """
        if not methods:
            methods = ["GET"]
        # Method OPTIONS needed for CORS
        if "OPTIONS" not in methods:
            methods.append("OPTIONS")
        methods = [method.upper() for method in methods]

        if parse_spec:
            api_spec = self._spec.get()
            if rpc:
                func = self._rpc_wrapper(func, is_async, api_spec=api_spec)
            else:
                func = self._local_wrapper(func, api_spec=api_spec)
        else:
            # Use either rpc or local wrapper to handle responses and exceptions
            func = self._rpc_wrapper(func, is_async) if rpc else self._local_wrapper(func)

        if validate:
            func = self._validate(func)
        elif validate_custom:
            func = self._validate_custom(func)

        func = self._authenticate(auth=auth, func=func, role=role)

        self._service.add_url_rule(
            route,
            view_func=func,
            endpoint=route + '_'.join(methods),
            provide_automatic_options=True,
            methods=methods)

    def validate_api_setup(self) -> None:
        """Validate the setup of the API with respect to the specification in the OpenAPI document.

        Raises:
            :py:class:`~gateway.dependencies.specs.OpenAPISpecException`: if the validation fails
        """
        try:
            self._spec.validate_api(self._service.url_map)
        except OpenAPISpecException as exp:
            self._service.logger.error(f" -> API setup is not valid: {exp}")
            exit(1)

    def _init_service(self) -> Flask:
        """Initialize the Flask application with configuration management.

        Returns:
            The instantiated :class:`~flask.Flask` object.
        """
        service = Flask(__name__)
        service.before_request(self.utils.fix_transfer_encoding)
        FlaskDynaconf(service)  # configure - set ENV_FOR_DYNACONF to select dev / prod / test (default: dev)

        return service

    def _init_rpc(self) -> FlaskPooledClusterRpcProxy:
        """Initialize the RPC proxy.

        Returns:
            The instantiated FlaskPooledClusterRpcProxy object
        """
        self._service.config.update({
            "NAMEKO_AMQP_URI":
                f"pyamqp://{settings.RABBIT_USER}:{settings.RABBIT_PASSWORD}"
                f"@{settings.RABBIT_HOST}:{settings.RABBIT_PORT}"
        })
        rpc = FlaskPooledClusterRpcProxy()
        rpc.init_app(self._service)
        return rpc

    def _init_response(self) -> ResponseParser:
        """Initialize and return the ResponseParser."""
        return ResponseParser(self._service.logger)

    def _init_specs(self) -> OpenAPISpecParser:
        """Initialize and return the OpenAPISpecParser."""
        return OpenAPISpecParser(self._res)

    def _init_auth(self) -> AuthenticationHandler:
        """Initialize and return the AuthenticationHandler."""
        return AuthenticationHandler(self._rpc, self._res)

    def _rpc_wrapper(self, f: MethodProxy, is_async: bool, **kwargs: Any) -> Callable:
        """The RPC decorator function handles communication with the RPC function.

        In detail responses and exception when communicating with the services are dealt with. This method is a single
        aggregated endpoint to handle the service communications.

        Args:
            f: The wrapped RPC function.
            is_async: Flags if the function should be executed asynchronously.

        Returns:
            Returns the decorator function or a HTTP error.
        """
        def decorator(**arguments: Any) -> Response:
            try:
                rpc_response = f.call_async(**arguments, **kwargs) if is_async else f(**arguments, **kwargs)

                if is_async:
                    # This currently just applies to POST /jobs/{job_id}/results
                    return self._res.parse({"code": 202})

                if rpc_response["status"] == "error":
                    rpc_response.pop("status")
                    return self._res.error(rpc_response)

                return self._res.parse(rpc_response)
            except Exception as exc:
                return self._res.error(exc)
        return decorator

    def _local_wrapper(self, f: Callable, **kwargs: Any) -> Callable:
        """The local decorator function handles responses and exception for non-RPC functions.

        Args:
            f: The wrapped local function.

        Returns:
            The decorator function or a HTTP error
        """
        def local_decorator(**arguments: Any) -> Union[Response, WerkzeugResponse]:
            try:
                local_response = f(**arguments, **kwargs)
                if not isinstance(local_response, dict) and local_response.status_code == 302:
                    # This is a redirect, pass repsonse as it is
                    # currently used only to redirect "/" to ".well-known/openeo"
                    return local_response

                if local_response["status"] == "error":
                    return self._res.error(local_response)
                elif local_response["status"] == "redirect":
                    return self._res.redirect_to(local_response["url"])
                return self._res.parse(local_response)

            except Exception as exc:
                return self._res.error(exc)

        return local_decorator

    def send_health_check(self, **kwargs: Any) -> dict:
        """Return the the sanity check.

        Returns:
            200 HTTP code.
        """
        return {
            "status": "success",
            "code": 200,
        }

    def send_openapi(self, **kwargs: Any) -> dict:
        """Return the parsed OpenAPI specification as JSON."""
        return {
            "status": "success",
            "code": 200,
            "data": self._spec.get(),
        }

    def send_redoc(self, **kwargs: Any) -> dict:
        """Return the ReDoc clients.

        Returns:
            The HTML file containing the ReDoc client setup.
        """
        return {
            "status": "success",
            "html": "redoc.html",
        }

    def main_page(self, api_spec: dict, **kwargs: Any) -> WerkzeugResponse:
        """Redirect main page "/" to openeo well known document "/.well-known/openeo".

        The well known openeo document must be served on a NOT versioned url.
        """
        base_url = api_spec["servers"][0]["url"]  # Without version - the first one!
        return redirect(base_url + "/.well-known/openeo")

    def _parse_error_to_json(self, exc: Exception) -> Response:
        """Serialize APIException to a Response object."""
        code = exc.code if hasattr(exc, "code") else 500
        return self._res.error(
            APIException(
                msg=str(exc),
                code=code,
                service="gateway",
                internal=False))
