"""Handle OpenAPISpecification including parsing, providing and raising corresponding error."""
import base64
import json
import uuid
from os import mkdir, path
from pathlib import Path
from re import match
from typing import Any, Callable, Dict, List, Tuple, Union

from dynaconf import settings
from flask import Response, request
from requests import get
from werkzeug.exceptions import BadRequest
from werkzeug.routing import Map
from yaml import full_load

from .response import APIException, ResponseParser


class OpenAPISpecException(Exception):
    """Raised if an Exception occurs while parsing the OpenAPI spec files or querying routes from the specifications."""

    def __init__(self, msg: str = None, code: int = 500, service: str = None, user_id: str = None,
                 internal: bool = True, links: list = None) -> None:
        """Initialize OpenAPiSpecException."""
        self._service = service if service else "gateway"
        self._user_id = user_id
        self._code = code
        self._msg = msg
        self._internal = internal
        self._links = links if links else [""]

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the object to a dict."""
        return {
            "status": "error",
            "service": self._service,
            "code": self._code,
            "user_id": self._user_id,
            "msg": self._msg,
            "internal": self._internal,
            "links": self._links
        }


class OpenAPISpecParser:
    """Parse the OpenAPI v3 specifications that are referred to in JSON files.

    The specifications can be queried for definitions of routes.

    Attributes:
        response_handler: The ResponseParser to parse an exception if parsing the API specs fails.
    """

    root_dir = Path(__file__).parent.parent.parent
    """Root folder of the gateway."""
    _openapi_file = str(root_dir) + "/openapi.yaml"
    """Absolute filepath to the openapi.yaml file"""
    _specs: dict = {}
    _specs_cache: dict = {}

    def __init__(self, response_handler: ResponseParser) -> None:
        """Initialize OpenAPISpecParser."""
        self.url_stack: List[str] = []
        self._parse_specs()
        self._res = response_handler

    def get(self) -> dict:
        """Returns the OpenAPI specification as dictionary."""
        return self._specs

    def validate_api(self, endpoints: Map) -> None:
        """Validated if the input endpoints are consistent to the OpenAPI specification of the Flask API gateway.

        This also includes the available HTTP options of the API.

        Args:
            endpoints: The endpoints of the API which should be validated.
        """
        # Methods that are validated (do not validate HEAD, OPTION)
        allowed_methods = ("get", "post", "put", "patch", "delete")

        # Extract the target specified blueprint of the API
        target: Dict[str, List[str]] = {}
        for endpoint, methods in self._specs["paths"].items():
            # Add versioning to ever URL. Exceptions:
            #  - "/.well-known/openeo" -> no versioning allowed
            #  - "/base" -> maps to "/" which redirects to "/.well-known/openeo"
            # Note that this still creates "/v1.0" which maps to "/" of the opeEO specs
            if not endpoint == '/.well-known/openeo':
                if endpoint == "/base":
                    endpoint = "/"
                else:
                    # Add versioning
                    endpoint = f"/{settings.OPENEO_VERSION}{endpoint}"
            target[endpoint] = []
            for method in methods:
                if method in allowed_methods:
                    target[endpoint].append(method.lower())

        # Extract the current status of the API
        status: Dict[str, List[str]] = {}
        for rule in endpoints.iter_rules():
            if not rule.rule.startswith("/static"):
                endpoint = rule.rule.replace("<", "{").replace(">", "}")
                if endpoint not in status:
                    status[endpoint] = []
                for method in rule.methods:
                    method = method.lower()
                    if method in allowed_methods:
                        status[endpoint].append(method)

        # Check if the target matches the status
        difference = set(target.keys()).symmetric_difference(status.keys())

        if len(difference) > 0:
            raise OpenAPISpecException(
                f"The gateway or specification is missing the endpoint(s) '{difference}'")

        for status_endpoint, status_methods in status.items():
            target_methods = target[status_endpoint]

            method_diff = set(target_methods).symmetric_difference(status_methods)
            if len(method_diff) > 0:
                raise OpenAPISpecException(f"The gateway or specification is missing the HTTP method(s) '{method_diff}'"
                                           f" at endpoint '{status_endpoint}'")

    def validate_custom(self, f: Callable) -> Callable:
        """Parses the provided parameters onward.

        Args:
            f: The function to be wrapped.

        Returns:
            The validator decorator.
        """
        def decorator(**kwargs: Any) -> Callable:
            if not request.json:
                params = {}
            else:
                params = request.json

            # Only needed /credentials/basic endpoint (needed data are in headers, not in data)
            if 'Authorization' in request.headers and 'Basic' in request.headers['Authorization']:
                encoded = request.headers['Authorization'].split(' ')[1]
                decoded = base64.b64decode(encoded).decode('utf8')
                params['username'], params['password'] = decoded.split(':')

            return f(**params)

        return decorator

    def validate(self, f: Callable) -> Callable:
        """Create a validator decorator for input parameters.

        Both parameters in the query and path of HTTP requests and the request bodies of e.g. POST requests are
        validated.

        Args:
            f: The function to be wrapped.

        Returns:
            The validator decorator.
        """
        def get_parameter_specs() -> Tuple[bool, dict, List[str]]:
            """Get the parameter specification for a request.

            Returns:
                A tuple with (1) a boolean flag if the request has specs, (2) a dictionary with the parameter specs and
                (3) a list of required parameters.
            """
            # Get the OpenAPI parameter specifications for the route and method
            req_path = str(request.url_rule).replace("<", "{").replace(">", "}")
            req_path = req_path.replace(f"/{settings.OPENEO_VERSION}", "")
            req_method = request.method.lower()
            route_specs = self._route(req_path)

            # Check if parameters required in request specification
            in_root = route_specs.keys() & {"parameters"}
            in_method = route_specs[req_method].keys() & {"parameters", "requestBody"}

            has_specs = bool(in_root) or bool(in_method)

            params_specs = {}
            param_required = []
            if has_specs:
                if in_root:
                    for p in route_specs["parameters"]:
                        if "required" in p:
                            param_required.append(p["name"])
                        if "schema" in p:
                            params_specs[p["name"]] = p["schema"]
                if in_method:
                    if "parameters" in in_method:
                        for p in route_specs[req_method]["parameters"]:
                            if "required" in p:
                                param_required.append(p["name"])
                            if "schema" in p:
                                params_specs[p["name"]] = p["schema"]
                    if "requestBody" in in_method:
                        content = route_specs[req_method]["requestBody"]["content"]
                        if content.get("application/json"):
                            body = content["application/json"]["schema"]
                        elif content.get("application/octet-stream"):
                            body = content["application/octet-stream"]["schema"]
                        else:
                            raise Exception(f"Input format {', '.join(content.keys())} is currently not supported")
                        if "required" in body:
                            param_required += body["required"]
                        if "properties" in body:
                            for p_key, p_value in body["properties"].items():
                                params_specs[p_key] = p_value

            return has_specs, params_specs, param_required

        def get_parameters() -> dict:
            """Return a dictionary including provided parameters.

            Raises:
                :class:`~gateway.dependencies.AAPIException`: if a BadRequest is raised.
            """
            try:
                parameters: Dict[str, Any] = {}

                if len(request.view_args) > 0:
                    parameters = {**parameters, **request.view_args}

                if len(request.args) > 0:
                    parameters = {**parameters, **request.args.to_dict(flat=True)}

                if request.data:
                    if request.headers['Content-Type'] == 'application/octet-stream':
                        parameters = {**parameters, **get_file_data()}
                    else:
                        parameters = {**parameters, **request.get_json()}
                return parameters
            except BadRequest:
                raise APIException(
                    msg="Error while parsing JSON in payload. Please make sure the JSON is valid.",
                    code=400,
                    service="gateway",
                    internal=False)

        def get_file_data() -> Dict[str, str]:
            """Return a dictionary with the path to the tmp file."""
            if not path.exists(settings.UPLOAD_TMP_DIR):
                mkdir(settings.UPLOAD_TMP_DIR)

            # Create a tmp file where the binary data is stored > does not need to be passed over the rabbit
            temp_file = path.join(settings.UPLOAD_TMP_DIR, str(uuid.uuid4()))
            with open(temp_file, 'wb') as file:
                file.write(request.data)
            return {"tmp_path": temp_file}

        def decorator(user: dict = None, **kwargs: Any) -> Union[Callable, Response]:
            """Return the provided function with added parameters if some are supplied.

            Currently validation is not implemented!
            """
            try:
                has_params, specs, required = get_parameter_specs()
                if not has_params:
                    return f(user=user)

                parameters = get_parameters()
                # TODO validation
                return f(user=user, **parameters)
            except Exception as exc:
                return self._res.error(exc)

        return decorator

    def _parse_specs(self) -> None:
        """Load the OpenAPI specifications from the YAML file and resolve all references in the document.

        Raises:
            :class:`~gateway.dependencies.spec.OpenAPIException`: If the openapi.yaml file does not exist.
        """
        if not path.isfile(self._openapi_file):
            raise OpenAPISpecException("Spec File '{0}' does not exist!".format(self._openapi_file))

        with open(self._openapi_file, "r") as yaml_file:
            specs = full_load(yaml_file)

        self._specs = self._parse_dict(specs, specs)
        self._specs_cache = {}

    def _map_type(self, in_type: Any) -> Callable:
        """Map the input types to the corresponding functions and return a lambda function that can be called.

        Args:
            The input value type.

        Returns:
            The mapped lambda function.
        """
        types = {
            dict: lambda value, ref: self._parse_dict(value, ref),
            list: lambda value, ref: self._parse_list(value, ref)
        }

        return types.get(in_type, lambda value, ref: value)

    def _parse_dict(self, in_dict: dict, ref: dict) -> dict:
        """Parse the input dict by resolving all references §ref that may be in included in it.

        The function is recursive.

        Args:
            in_dict: The input dict.
            ref: The base reference schema.

        Returns:
            The parsed output dict.
        """
        out_dict = {}
        for key, value in in_dict.items():
            # Don't parse oneOf, keys as these might be recursive
            if key == "oneOf":
                out_dict[key] = value
            elif key == "$ref" and isinstance(value, str):
                return self._parse_ref(value, ref)
            elif isinstance(key, str) and key.startswith('x-'):
                out_dict[key[2:]] = self._map_type(type(value))(value, ref)
            else:
                out_dict[key] = self._map_type(type(value))(value, ref)
        return out_dict

    def _parse_list(self, in_list: list, ref: dict) -> list:
        """Parse a list object by iterating each element and parsing it based on its type.

        The function is recursive.

        Args:
            in_list: The input list.
            ref: The base reference schema.

        Returns:
            The parsed output list.
        """
        out_list = []
        for value in in_list:
            out_list.append(self._map_type(type(value))(value, ref))
        return out_list

    def _parse_ref(self, in_url: str, ref: dict) -> dict:
        """Parse the references that are passed to the function.

        The reference may point to the input base reference schema or an external schema. External schemas are
        downloaded and parsed. Download schemas are cached to improve the processing speed.
        The function is recursive.

        Arguments:
            in_url: The input URL.
            ref: The base reference schema.

        Returns:
            The parsed dict containing all resolved references.
        """
        self.url_stack.insert(0, in_url)
        if self._is_repeated_recursion():
            return {'recursive': ''}

        url_split = in_url.split("#")
        url = url_split[0]

        # Parse encoded characters
        path = []
        for p_el in url_split[1].split("/"):
            if p_el:
                path.append(p_el.replace('~0', '~').replace('~1', '/'))

        # If it is a local reference use base ref schema, else download the reference, if it is
        # not included in the specification cache
        if not url:
            element = ref
        else:
            if url not in self._specs_cache:
                response = get(url)
                if not response.status_code == 200:
                    raise OpenAPISpecException("Spec File '{0}' does not exist!".format(url))
                try:
                    self._specs_cache[url] = response.json()
                except json.JSONDecodeError:
                    # openEO 1.0.0 uses yaml instead of json for reference specs
                    # TODO once each endpoint uses 1.0.0 the file should be directly loaded as yaml
                    self._specs_cache[url] = full_load(response.text)

            ref = self._specs_cache[url]
            element = self._specs_cache[url]

        # Find the referenced element and parse it recursively
        for p in path:
            # Check for array reference e.g. /collections/parameters[0]
            if match(r"\w*\[\d+\]$", p):
                parts = p.split("[")
                idx = int(parts[1][:-1])
                element = element[parts[0]][idx]
            else:
                element = element[p]

        element = self._map_type(type(element))(element, ref)
        del self.url_stack[0]
        return element

    def _is_repeated_recursion(self) -> bool:
        """Check for recursive calls.

        There are both case where objects can be stored recursively within themselves and where objects call each other
        mutually. To prevent endless recursion a dict {'recursive': ''} is returned when the same url pattern is
        detected within a recursion stack.

        Returns:
            Whether last url is part of an already existing url stack.
        """
        new_url = self.url_stack[0]
        pattern = [new_url]
        for i, cur_url in enumerate(self.url_stack):
            if i == 0:
                continue
            if cur_url == new_url:
                return True
            else:
                pattern.append(cur_url)
        return False

    def _route(self, route: str) -> dict:
        """Return the OpenAPI specification for the requested route.

        Args:
            route: The route (e.g. '/processes')

        Returns:
            Returns the matching specification
        """
        for oe_route, methods in self._specs["paths"].items():
            if oe_route == route:
                return methods
        raise OpenAPISpecException(f"Specification of route '{route}' does not exist.")
