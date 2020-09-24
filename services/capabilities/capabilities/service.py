"""Provides the implementation of the capabilities discovery service and service exception.

This is the main entry point to the capabilities discovery.
"""

import logging
from typing import Any, Dict, Optional

from nameko.rpc import rpc

from capabilities.dependencies.settings import initialise_settings

service_name = "capabilities"
LOGGER = logging.getLogger('standardlog')
initialise_settings()


class ServiceException(Exception):
    """ServiceException is raised if an exception occurred while processing the request.

    The ServiceException is mapping any exception to a serializable format for the API gateway.

    Attributes:
        service: The name of the service as string.
        code: An integer holding the error code.
        user_id: The id of the user as string. (default: None)
        msg: A string with the error message.
        internal: A boolean indicating if this is an internal error. (default: True)
        links: A list of links which can be useful when getting this error. (default: None)
    """

    def __init__(self, service: str, code: int, user_id: Optional[str], msg: str, internal: bool = True,
                 links: list = None) -> None:
        """Initialise ServiceException."""
        if not links:
            links = []
        self._service = service
        self._code = code
        self._user_id = user_id
        self._msg = msg
        self._internal = internal
        self._links = links
        LOGGER.exception(msg, exc_info=True)

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


class CapabilitiesService:
    """Discovery of capabilities that are available at the back-end.

    This class implements a nameko microservice and therefore provides a set of rpc methods which describe the
    capabilities of the backend.
    """

    name: str = service_name
    """The name of the CapabilitiesService.

    This name is used when an exception occurs to set the service name in the exception.
    """

    @rpc
    def send_index(self, api_spec: dict, user: Dict[str, Any] = None) -> dict:
        """Returns a dictionary containing the available routes and HTTP methods at the backend.

        The information is taken from the provided OpenAPI Specification.

        Args:
            api_spec: OpenAPI Specification
            user: User Id (not needed, exists for compatibility reasons)

        Returns:
            A dictionary containing the API capabilities
        """
        # TODO: Implement billing plans

        try:
            endpoints = []
            # Remove /.well-known/openeo endpoint, must not be listed under versioned URLs
            if '/.well-known/openeo' in api_spec['paths']:
                _ = api_spec['paths'].pop('/.well-known/openeo')
            if '/base' in api_spec['paths']:
                _ = api_spec['paths'].pop('/base')
            for path_name, methods in api_spec["paths"].items():
                path_to_replace = path_name[path_name.find(':'):path_name.find('}')]
                path_name = path_name.replace(path_to_replace, '')
                endpoint = {"path": path_name, "methods": []}
                for method_name, _ in methods.items():
                    if method_name in ("get", "post", "patch", "put", "delete"):
                        endpoint["methods"].append(method_name.upper())
                endpoints.append(endpoint)

            capabilities = {
                "api_version": api_spec["info"]["version"],
                "backend_version": api_spec["info"]["backend_version"],
                "title": api_spec["info"]["title"],
                "description": api_spec["info"]["description"],
                "endpoints": endpoints,
                "stac_version": api_spec["info"]["stac_version"],
                "id": api_spec["info"]["id"],
                "links": [],  # TODO add links
                "production": api_spec["info"]["production"],
            }

            return {
                "status": "success",
                "code": 200,
                "data": capabilities,
            }

        except Exception as exp:
            return ServiceException(CapabilitiesService.name, 500, self._get_user_id(user), str(exp)).to_dict()

    @rpc
    def get_versions(self, api_spec: dict, user: Dict[str, Any] = None) -> dict:
        """Lists OpenEO API versions available at the back-end.

        The information is taken from the provided OpenAPI Specification.
        The provided versions exactly match versions defined here (https://github.com/Open-EO/openeo-api)

        Args:
            api_spec: OpenAPI Specification
            user: User (not needed, exists for compatibility reasons)

        Returns:
            Contains the supported OpenEO API versions
        """
        try:
            # NB The api 'versions' must match exactly the version numbers available here:
            # https://github.com/Open-EO/openeo-api
            api_versions = []
            for server in api_spec["servers"][1:]:
                this_version = {
                    "production": api_spec["info"]["production"],
                    "url": server["url"],
                    "api_version": server["description"].split(" ")[-1]
                }
                api_versions.append(this_version)

            return {
                "status": "success",
                "code": 200,
                "data": {
                    "versions": api_versions
                }
            }

        except Exception as exp:
            return ServiceException(CapabilitiesService.name, 500, self._get_user_id(user), str(exp)).to_dict()

    @rpc
    def get_file_formats(self, api_spec: dict, user: Dict[str, Any] = None) -> dict:
        """Lists input / output file formats available at the back-end.

        The information is taken from the provided OpenAPI Specification.

        Args:
            api_spec: OpenAPI Specification
            user: User (not needed, exists for compatibility reasons)

        Returns:
            Describes all supported input / output file formats
        """
        def get_dict(file_fmts: dict) -> dict:
            final_fmt = {}
            for fmt in file_fmts:
                final_fmt[fmt["name"]] = {
                    "title": fmt.get("title", None),
                    "gis_data_types": fmt["gis_data_types"],
                    "parameters": fmt.get("parameters", {})
                }
            return final_fmt

        try:
            file_formats = api_spec["info"]["file_formats"]

            return {
                "status": "success",
                "code": 200,
                "data": {
                    "output": get_dict(file_formats["output"]),
                    "input": get_dict(file_formats["input"]),
                },
            }
        except Exception as exp:
            return ServiceException(CapabilitiesService.name, 500, self._get_user_id(user), str(exp)).to_dict()

    @rpc
    def get_udfs(self, api_spec: dict, user: Dict[str, Any] = None) -> dict:
        """Lists UDFs available at the back-end.

        The information is taken from the provided OpenAPI Specification.

        Args:
            api_spec: OpenAPI Specification
            user: User (not needed, exists for compatibility reasons)

        Returns:
            Contains detailed description about the supported UDF runtimes
        """
        try:
            udf_all = api_spec["info"]["udf"]

            return {
                "status": "success",
                "code": 200,
                "data": udf_all,
            }
        except Exception as exp:
            return ServiceException(CapabilitiesService.name, 500, self._get_user_id(user), str(exp)).to_dict()

    @rpc
    def get_service_types(self, api_spec: dict, user: Dict[str, Any] = None) -> dict:
        """Lists service types available at the back-end.

        Currently no secondary services are implemented, therefore are default of 'None implemented' is returned.
        Once secondary services are implemented they will we described in the OpenAPI Specification and returned here.

        Args:
            api_spec: OpenAPI Specification - will be needed once secondary services are implemented to get there
                description.
            user: User (not needed, exists for compatibility reasons)

        Returns:
            Contains supported secondary services
        """
        try:
            return {
                "status": "success",
                "code": 200,
                "data": {'Secondary services': 'None implemented.'},
            }
        except Exception as exp:
            return ServiceException(CapabilitiesService.name, 500, self._get_user_id(user), str(exp)).to_dict()

    def _get_user_id(self, user: Optional[Dict[str, Any]]) -> Optional[str]:
        """Returns the user_id if user object is set."""
        return user["id"] if user and "id" in user else None
