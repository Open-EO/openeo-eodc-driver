""" OpenAPISpecParser, OpenAPISpecException """

from os import path
from pathlib import Path
from sys import modules
from flask import request
from werkzeug.exceptions import BadRequest
from yaml import load
from requests import get
from typing import Callable, Any
from re import match

from .response import APIException


class OpenAPISpecException(Exception):
    """The OpenAPISpecParserException throws if an Exception occures while parsing from the
    OpenAPI spec files or querying routes from the specifications.
    """
    pass


class OpenAPISpecParser:
    """The OpenAPISpecParser parses the OpenAPI v3 specifcations that are referred in JSON files.
    The specifications can be queried for definitions of routes. 
    """

    root_dir = Path(__file__).parent.parent.parent
    _openapi_file = str(root_dir) + "/openapi.yaml"
    _specs = {}
    _specs_cache = {}

    def __init__(self, response_handler):
        self._parse_specs()
        self._res = response_handler
    
    def get(self):
        """Returns the OpenAPI specification
        """

        return self._specs
    
    def validate_api(self, endpoints:object):
        """Validated if the input endpoints and the available HTTP options
        of the API are consistent to the OpenAPI specification of the Flask 
        API gateway.

        Arguments:
            endpoints {object} -- The endpoints of the API
        """

        # Methods that are validated (do not validate HEAD, OPTION)
        allowed_methods = ("get", "post", "put", "patch", "delete")

        # Extract the target specified blueprint of the API
        target = {}
        for endpoint, methods in self._specs["paths"].items():
            target[endpoint] = []
            for method in methods:
                if method in allowed_methods:
                    target[endpoint].append(method.lower())

        # Extract the current status of the API
        status = {}
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
            raise OpenAPISpecException("The gateway or specification is missing the endpoint(s) '{0}'".format(str(difference)))

        for status_endpoint, status_methods in status.items():
            target_methods = target[status_endpoint]

            method_diff = set(target_methods).symmetric_difference(status_methods)
            if len(method_diff) > 0:
                raise OpenAPISpecException("The gateway or specification is missing the HTTP method(s) '{0}' at endpoint '{1}'".format(str(method_diff), status_endpoint))               
    
    def validate(self, f:Callable) -> Callable:
        """Creates a validator decorator for the input parameters in the query and path of HTTP requests 
        and the request bodies of e.g. POST requests.
        
        Arguments:
            f {Callable} -- The function to be wrapped
        
        Returns:
            Callable -- The validator decorator
        """

        def get_parameter_specs():
            # Get the OpenAPI parameter specifications for the route and method
            req_path = str(request.url_rule).replace("<","{").replace(">","}")
            req_method = request.method.lower()
            route_specs = self._route(req_path)

            # Check if parameters requried in request specification
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
                        body = route_specs[req_method]["requestBody"]["content"]["application/json"]["schema"]
                        if "required" in body:
                            param_required  += body["required"]
                        if "properties" in body:
                            for p_key, p_value in body["properties"].items():
                                params_specs[p_key] = p_value

            return has_specs, params_specs, param_required
        
        def get_parameters():
            try:
                parameters = {}

                if len(request.view_args) > 0:
                    parameters = {**parameters, **request.view_args}

                if len(request.args) > 0:
                    parameters = {**parameters, **request.args.to_dict(flat=True)}
                
                if request.data:
                    parameters = {**parameters, **request.get_json()}
                
                return parameters
            except BadRequest as exp:
                raise APIException(
                    msg="Error while parsing JSON in payload. Please make sure the JSON is valid.", 
                    code=400, 
                    service="gateway", 
                    internal=False)
            
            

        def decorator(user_id=None, **kwargs):

            type_map = {
                "integer": lambda x: int(x),
                "float": lambda x: float(x),
                "double": lambda x: float(x),
                "boolean": lambda x: bool(x),
                "string": lambda x: str(x)
            }

            try:
                has_params, specs, required = get_parameter_specs()

                if not has_params:
                    return f(user_id=user_id)

                parameters = get_parameters()

                parsed_params = {}
                for p_name, p_specs in specs.items():
                    if p_name not in parameters.keys():
                        if p_name in required:
                            if "default" in p_specs:
                                parsed_params[p_name] = p_specs["default"]
                            else:
                                msg = "Missing parameter {0}.".format(p_name)
                                raise APIException(msg=msg, code=400, service="gateway", internal=False)
                    else:
                        p_value = parameters[p_name]

                        if "type" in p_specs:
                            p_value = type_map.get(p_specs["type"], lambda x: x)(p_value)
                        
                        if "pattern" in p_specs:
                            if not match(p_specs["pattern"], p_value):
                                msg = "Parameter {0} does not match pattern {1}.".format(p_name, p_specs["pattern"])
                                raise APIException(msg=msg, code=400, service="gateway", internal=False)

                        if "enum" in p_specs:
                            if not p_value in p_specs["enum"]:
                                msg = "Parameter {0} does not match enum item {1}.".format(p_name, p_specs["enum"])
                                raise APIException(msg=msg, code=400, service="gateway", internal=False)
                        
                        parsed_params[p_name] = p_value
    
                return f(user_id=user_id, **parsed_params)
            except Exception as exc:
                return self._res.error(exc)
        return decorator

    def _parse_specs(self):
        """Load the OpenAPI specifications from the YAML file and resolve all references in the
        document
        """

        if not path.isfile(self._openapi_file):
            raise OpenAPISpecException("Spec File '{0}' does not exist!".format(self._openapi_file))
        
        with open(self._openapi_file, "r") as yaml_file:
            specs = load(yaml_file)
        
        self._specs = self._parse_dict(specs, specs)
        self._specs_cache = {}

    def _map_type(self, in_type:Any) -> Callable:
        """Maps the input types to the corresponding functions and 
        returns a lambda function that can be called.
        
        Arguments:
            in_type {Any} -- The input value type
        
        Returns:
            Callable -- The mapped lambda function
        """

        types = {
            dict: lambda value, ref: self._parse_dict(value, ref),
            list: lambda value, ref: self._parse_list(value, ref)
        }

        return types.get(in_type, lambda value, ref: value)
    
    def _parse_dict(self, in_dict:dict, ref:dict) -> dict:
        """Parses the input dict by resolving all references §ref that may
        be in included in it.

        The function is recursive.
        
        Arguments:
            in_dict {dict} -- The input dict
            ref {dict} -- The base reference schema
        
        Returns:
            dict -- The parsed output dict
        """

        out_dict = {}
        for key, value in in_dict.items():
            # Don't parse oneOf, keys as these might be recursive
            if key == "oneOf":
                out_dict[key] = value
            elif key == "$ref" and isinstance(value, str):
                return self._parse_ref(value, ref)
            else:
                out_dict[key] = self._map_type(type(value))(value, ref)
        return out_dict

    def _parse_list(self, in_list:list, ref:dict) -> list:
        """Parses a list object by iterating each element and parsing it
        based on its type.

        The function is recursive.
        
        Arguments:
            in_list {list} -- The input list
            ref {dict} -- The base reference schema
        
        Returns:
            list -- The parsed output list
        """

        out_list = []
        for value in in_list:
            out_list.append(self._map_type(type(value))(value, ref))
        return out_list
    
    def _parse_ref(self, in_url:str, ref:dict) -> dict:
        """Parses the references that are passed to the function. The reference
        may point to the input base reference schema or an external schema. External 
        schemas are downloaded and parsed. Download schemas are cached to improve the
        processing speed.

        The function is recursive.
        
        Arguments:
            in_url {str} -- The input URL
            ref {dict} -- The base reference schema
        
        Returns:
            dict -- The paresed dict containing all resolved references
        """

        url_split = in_url.split("#")
        url = url_split[0]

        # Parse encoded characters
        path = []
        for p_el in url_split[1].split("/"):
            if p_el: path.append(p_el.replace('~0', '~').replace('~1', '/'))
        
        # If it is a local reference use base ref schema, selse dowload teh reference, if it is
        # not included in the specification chache
        if not url:
            element = ref
        else:
            if not url in self._specs_cache:
                response = get(url)
                if not response.status_code == 200:
                    raise OpenAPISpecException("Spec File '{0}' does not exist!".format(url))
                self._specs_cache[url] = response.json()

            ref = self._specs_cache[url]
            element = self._specs_cache[url]
        
        # Find the referenced element and parse it recursively
        for p in path:
            # Check for array refference e.g. /collections/parameters[0]
            if match(r"\w*\[\d+\]$", p):
                p = p.split("[")
                idx = int(p[1][:-1])
                element = element[p[0]][idx]
            else:
                element = element[p]
        
        element = self._map_type(type(element))(element, ref)
        return element
    
    def _route(self, route:str) -> dict:
        """Returns the OpenAPI specification for the requested route.
        
        Arguments:
            route {str} -- The route (e.g. '/processes')
        
        Returns:
            dict -- Returns the matching specification
        """

        for oe_route, methods in self._specs["paths"].items():
            if oe_route == route:
                return methods

        raise OpenAPISpecException("Specification of route '{0}' " \
                                   "does not exist".format(route))
    