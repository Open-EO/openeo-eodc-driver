""" Capabilities Discovery """
from nameko.rpc import rpc
import logging

service_name = "capabilities"
LOGGER = logging.getLogger('standardlog')

class ServiceException(Exception):
    """ServiceException raises if an exception occured while processing the
    request. The ServiceException is mapping any exception to a serializable
    format for the API gateway.
    """

    def __init__(self, service: str, code: int, user_id: str, msg: str, internal: bool=True, links: list=None):
        if not links:
            links = []
        self._service = service
        self._code = code
        self._user_id = user_id
        self._msg = msg
        self._internal = internal
        self._links = links
        LOGGER.exception(msg, exc_info=True)

    def to_dict(self) -> dict:
        """Serializes the object to a dict.

        Returns:
            dict -- The serialized exception
        """
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
    """

    name = service_name

    @rpc
    def get_versions(self, user_id: str=None):
        """Lists OpenEO API versions available at the back-end.
        """
        try:
            return {
                "status": "success",
                "code": 200,
                "data": {
                    "versions": [
                        {
                            "url": "https://openeo.eodc.eu",
                            "api_version": "0.4.0",
                        }
                    ]
                }
            }

        except Exception as exp:
            return ServiceException(CapabilitiesService.name, 500, user_id, str(exp)).to_dict()

    @rpc
    def get_output_formats(self, user_id: str=None):
        """Lists output formats available at the back-end.
        """
        try:
            default_out = {
                "GTiff": {
                  "gis_data_types": [
                    "raster"
                  ],
                  "parameters": {}
                },
                "png": {
                  "gis_data_types": [
                    "raster"
                  ],
                  "parameters": {}
                },
                "jpeg": {
                  "gis_data_types": [
                    "raster"
                  ],
                  "parameters": {}
                }
              }
            return {
                "status": "success",
                "code": 200,
                "data": default_out,
            }
        except Exception as exp:
            return ServiceException(CapabilitiesService.name, 500, user_id, str(exp)).to_dict()

    @rpc
    def get_udfs(self, user_id: str=None):
        """Lists UDFs available at the back-end.
        """
        try:
            return {
                "status": "success",
                "code": 200,
                "data": {},
            }
        except Exception as exp:
            return ServiceException(CapabilitiesService.name, 500, user_id, str(exp)).to_dict()

    @rpc
    def get_service_types(self, user_id: str=None):
        """Lists service types available at the back-end.
        """
        try:
            return {
                "status": "success",
                "code": 200,
                "data": {},
            }
        except Exception as exp:
            return ServiceException(CapabilitiesService.name, 500, user_id, str(exp)).to_dict()
