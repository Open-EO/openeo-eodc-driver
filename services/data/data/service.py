"""Provides the implementation of the EO data discovery service and service exception.

This is the main entry point to the EO data discovery.
"""

import json
import logging
import os
from pprint import pformat
from typing import Any, Dict, Optional

from nameko.rpc import rpc

from .dependencies.csw import CSWSession, CSWSessionDC
from .dependencies.settings import initialise_settings
from .schemas import CollectionSchema, CollectionsSchema

service_name = "data"
LOGGER = logging.getLogger("standardlog")
initialise_settings()


class ServiceException(Exception):
    """ServiceException is raised if an exception occurred while processing the request.

    The ServiceException is mapping any exception to a serializable format for the API gateway.
    Attributes:
        code: An integer holding the error code.
        user_id: The id of the user as string. (default: None)
        msg: A string with the error message.
        internal: A boolean indicating if this is an internal error. (default: True)
        links: A list of links which can be useful when getting this error. (default: None)
    """

    def __init__(
            self, code: int, user_id: Optional[str], msg: str, internal: bool = True, links: list = None
    ) -> None:
        """Initialize data service ServiceException."""
        self._service = service_name
        self._code = code
        self._user_id = user_id if user_id else "None"
        self._msg = msg
        self._internal = internal
        self._links = links if links else []
        LOGGER.exception(msg, exc_info=True)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the object to a dict.

        Returns:
            The serialized exception
        """
        return {
            "status": "error",
            "service": self._service,
            "code": self._code,
            "user_id": self._user_id,
            "msg": self._msg,
            "internal": self._internal,
            "links": self._links,
        }


class DataService:
    """Discovery of Earth observation datasets that are available at the backend."""

    name = service_name
    csw_session = CSWSession()
    """CSWHandler dependency injected into the service."""
    csw_session_dc = CSWSessionDC()
    """Second CSWHandler dependency also injected into the service.

    This is only a midterm solution to support two CSW servers.
    """

    def __init__(self) -> None:
        """Initialize Data Service."""
        LOGGER.info(f"Initialized {self}")

    def __repr__(self) -> str:
        """Return human readable version of the service."""
        return f"DataService('{self.name}')"

    @rpc
    def get_all_products(self, user: Dict[str, Any] = None) -> dict:
        """Return available datasets with basic information about them.

        The returned basic information includes for instance an unique identifier per dataset which can be used to get
        more detailed information.
        Depending on whether a user is given or not also private datasets may be returned. This depends on whether
        the user has required access rights. If no user is defined only public datasets are returned.

        Args:
            user: User - determines which datasets are returned.

        Returns:
             A dictionary with a list of products or a serialized exception.
        """
        LOGGER.info("All products requested")
        LOGGER.debug("user_id requesting %s", self._get_user_id(user))
        try:
            product_records = self.csw_session.get_all_products()
            if user and self.csw_session_dc.data_access in user["profile"]["data_access"]:
                acube_collections = self.csw_session_dc.get_all_products()
                for col in acube_collections[0]:
                    product_records[0].append(col)

            response = CollectionsSchema().dump(product_records)

            LOGGER.debug("response:\n%s", pformat(response))
            return {"status": "success", "code": 200, "data": response}
        except Exception as exp:
            return ServiceException(
                500,
                self._get_user_id(user),
                str(exp),
                links=["#tag/EO-Data-Discovery/paths/~1data/get"],
            ).to_dict()

    @rpc
    def get_product_detail(
            self, collection_id: str, user: Dict[str, Any] = None
    ) -> dict:
        """Return detailed information about a dataset.

        Depending on whether or not a user is given also private datasets may be accessible.

        Args:
            user: User (optional), determines which dataset are available.
            collection_id: The identifier of a dataset.

        Returns:
            Detailed information about a dataset as dictionary or a serialized exception.
        """
        try:
            LOGGER.info("%s product requested", collection_id)
            product_record = self.csw_session.get_product(collection_id)

            if collection_id in ('TUW_SIG0_S1'):
                # Check user permission
                error_code = None
                if not user:
                    error_code = 401  # Unauthorized
                    error_msg = "This collection is not publicly accessible."
                if user and self.csw_session_dc.data_access not in user["profile"]["data_access"]:
                    error_code = 403  # Forbidden (dpes not have permissions)
                    error_msg = "User is not authorized to access this collection."
                if error_code:
                    return ServiceException(
                        error_code,
                        self._get_user_id(user),
                        error_msg,
                        internal=False,
                        links=[],
                    ).to_dict()

            response = CollectionSchema().dump(product_record)

            # Add cube:dimensions and summaries
            # TODO these fields should be added to the cached JSONs when writing them to disk
            json_file = os.path.join(
                os.path.dirname(__file__),
                "dependencies",
                "jsons",
                collection_id + ".json",
            )
            if os.path.isfile(json_file):
                with open(json_file) as file_json:
                    json_data = json.load(file_json)
                    for key in json_data.keys():
                        response[key] = json_data[key]

            LOGGER.debug("response:\n%s", pformat(response))
            return {"status": "success", "code": 200, "data": response}
        except Exception as exp:
            return ServiceException(500, self._get_user_id(user), str(exp)).to_dict()

    @rpc
    def refresh_cache(self, user: Dict[str, Any] = None, use_cache: bool = False) -> dict:
        """Refresh the cache of dataset information.

        Args:
            user: User (not needed, exists for compatibility reasons)
            use_cache: Whether the existing cache is used or data is refreshed.

        Returns:
            Success message or Exception.
        """
        try:
            LOGGER.info("Refresh cache requested")
            self.csw_session.refresh_cache(use_cache)
            self.csw_session_dc.refresh_cache(use_cache)

            return {
                "status": "success",
                "code": 200,
                "data": {"message": "Successfully refreshed cache"},
            }
        except Exception as exp:
            return ServiceException(500, self._get_user_id(user), str(exp)).to_dict()

    def _get_user_id(self, user: Optional[Dict[str, Any]]) -> Optional[str]:
        """Return the user_id if user object is set."""
        return user["id"] if user and "id" in user else None
