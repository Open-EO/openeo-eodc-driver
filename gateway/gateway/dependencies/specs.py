""" OpenAPISpecParser, OpenAPISpecException """

from os import path
from sys import modules
from flask import request
from yaml import load
from requests import get
from typing import Callable, Any
from re import match


class OpenAPISpecException(Exception):
    """The OpenAPISpecParserException throws if an Exception occures while parsing from the
    OpenAPI spec files or querying routes from the specifications.
    """
    pass


class OpenAPISpecParser:
    """The OpenAPISpecParser parses the OpenAPI v3 specifcations that are referred in JSON files.
    The specifications can be queried for definitions of routes. 
    """

    _openapi_file = path.dirname(modules['__main__'].__file__) + "\\openapi.yaml"
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
                status[rule.rule] = []
                for method in rule.methods:
                    method = method.lower()
                    if method in allowed_methods:
                        status[rule.rule].append(method)
        
        # Check if the target matches the status
        routes_valid = target.keys() == status.keys()

        if not routes_valid:
            raise OpenAPISpecException("The endpoints in the specification and the current endpoints do not match!")

        for status_endpoint, status_methods in status.items():
            target_methods = target[status_endpoint]

            if not status_methods == target_methods:
                raise OpenAPISpecException("The endpoint '{0}' does not possess the specified HTTP methods".format(status_endpoint))
    
    def validate(self, f:Callable) -> Callable:
        """Creates a validator decorator for the input parameters in teh query and path of HTTP requests 
        and the request bodies of e.g. POST requests.
        
        Arguments:
            f {Callable} -- The function to be wrapped
        
        Returns:
            Callable -- The validator decorator
        """

        def decorator(user_id=None):

            type_map = {
                "integer": lambda x: int(x),
                "string": lambda x: str(x)
            }

            params_map = {
                "path": lambda req: req.view_args,
                "query": lambda req: req.args,
                "body": lambda req: req.get_json(),
            }

            try:
                parsed_params = {}

                req_path = str(request.url_rule).replace("<","{").replace(">","}")
                req_method = request.method.lower()

                # Get the OpenAPI parameter specifications for the route and method
                route_specs = self._route(req_path)

                in_root = "parameters" in route_specs
                in_method = "parameters" in route_specs[req_method]
                
                if not in_root and not in_method:
                    return f(user_id)
                
                parameter_specs = []
                if in_root:
                    parameter_specs += route_specs["parameters"]
                
                if in_method:
                    parameter_specs += route_specs[req_method]["parameters"]

                if len(parameter_specs) == 0:
                    return f(user_id)

                for p_spec in parameter_specs:
                    parameters = params_map[p_spec["in"]](request)

                    if p_spec["name"] not in parameters:
                        if "required" in p_spec and p_spec["required"]:
                            raise OpenAPISpecException("Missing parameter {0}.".format(p_spec["name"]))

                    p_value =  parameters[p_spec["name"]]
                    if "schema" in p_spec:
                        if "type" in p_spec["schema"]:
                            p_value = type_map[p_spec["schema"]["type"]](p_value)
                        if "pattern" in p_spec["schema"]:
                            if not match(p_spec["schema"]["pattern"], p_value):
                                raise OpenAPISpecException("Parameter {0} does not match pattern {1}."\
                                                            .format(p_spec["name"], p_spec["schema"]["pattern"]))
                    
                    parsed_params[p_spec["name"]] = p_value
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
            if key == "$ref" and isinstance(value, str):
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
    