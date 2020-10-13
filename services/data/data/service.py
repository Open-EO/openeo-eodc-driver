"""Provides the implementation of the EO data discovery service and service exception.

This is the main entry point to the EO data discovery.
"""

import logging
from pprint import pformat
from typing import Any, Dict, List, Optional

from dynaconf import settings
from nameko.rpc import rpc

from .dependencies.csw import CSWSession, CSWSessionDC
from .dependencies.settings import initialise_settings
from .dependencies.wekeo_hda import HDASession
from .models import Collections
from .schema import CollectionSchema, CollectionsSchema

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
            The serialized exception.
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
    if settings.IS_CSW_SERVER:
        csw_session = CSWSession()
        """CSWHandler dependency injected into the service."""
    if settings.IS_CSW_SERVER_DC:
        csw_session_dc = CSWSessionDC()
        """Second CSWHandler dependency also injected into the service.

        This is only a midterm solution to support two CSW servers.
        """
    if settings.IS_HDA_WEKEO:
        hda_session = HDASession()
        """HDAHandler dependency injected into the service."""

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
            all_collections = Collections(collections=[], links=[])
            if settings.IS_CSW_SERVER:
                csw_collections = self.csw_session.get_all_products()
                for col in csw_collections[0]:
                    all_collections[0].append(col)
            if settings.IS_CSW_SERVER_DC and \
               user and \
               self.csw_session_dc.data_access in user["profile"]["data_access"]:
                acube_collections = self.csw_session_dc.get_all_products()
                for col in acube_collections[0]:
                    all_collections[0].append(col)
            if settings.IS_HDA_WEKEO:
                wekeo_collections = self.hda_session.get_all_products()
                for col in wekeo_collections[0]:
                    all_collections[0].append(col)

            response = CollectionsSchema().dump(all_collections)

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

            product_record = None
            if settings.IS_CSW_SERVER and collection_id in settings.WHITELIST:
                product_record = self.csw_session.get_product(collection_id)
            elif settings.IS_CSW_SERVER_DC and collection_id in settings.WHITELIST_DC:
                product_record = self.csw_session_dc.get_product(collection_id)
            elif settings.IS_HDA_WEKEO and collection_id in settings.WHITELIST_WEKEO:
                product_record = self.hda_session.get_product(collection_id)
            if not product_record:
                return ServiceException(400, self._get_user_id(user),
                                        f"The requested collection {collection_id} does not exist on the backend.",
                                        internal=False, links=[]).to_dict()

            # Check user permission
            # TODO: implement better logic for checking user permissions
            # Unauthorized
            if collection_id in ('TUW_SIG0_S1') and not user:
                return ServiceException(401, self._get_user_id(user), "This collection is not publicly accessible.",
                                        internal=False, links=[]).to_dict()
            # Forbidden (does not have permissions)
            elif collection_id == 'TUW_SIG0_S1' and user \
                    and self.csw_session_dc.data_access not in user["profile"]["data_access"]:
                return ServiceException(403, self._get_user_id(user),
                                        "User is not authorized to access this collection.", internal=False,
                                        links=[]).to_dict()

            response = CollectionSchema().dump(product_record)
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
            if settings.IS_CSW_SERVER:
                self.csw_session.refresh_cache(use_cache)
            if settings.IS_CSW_SERVER_DC:
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

    @rpc
    def get_filepaths(self, collection_id: str, spatial_extent: List[float], temporal_extent: List[str],
                      user: Dict[str, Any] = None) -> Dict:
        """Return a list of filepaths.

        Keyword Arguments:
            user {Dict[str, Any]} -- The user (default: {None})
            collecion_id {str} -- identifier of the collection
            spatial_extent {List[float]} -- bounding box [ymin, xmin, ymax, ymax]
            temporal_extent {List[str]} -- e.g. ["2018-06-04", "2018-06-23"]

        Returns:
            dict -- Success message or Exception
        """
        try:
            filepaths = {}
            if settings.IS_CSW_SERVER and collection_id in settings.WHITELIST:
                filepaths['filepaths'] = self.csw_session.get_filepaths(collection_id, spatial_extent, temporal_extent)
            elif settings.IS_CSW_SERVER_DC and collection_id in settings.WHITELIST_DC:
                filepaths['filepaths'] = self.csw_session_dc.get_filepaths(collection_id, spatial_extent, temporal_extent)
            elif settings.IS_HDA_WEKEO and collection_id in settings.WHITELIST_WEKEO:
                filepaths['filepaths'], filepaths['wekeo_job_id'] = \
                    self.hda_session.get_filepaths(collection_id, spatial_extent, temporal_extent)

            if not filepaths:
                msg = "No filepaths were found."
                return ServiceException(500, self._get_user_id(user), msg=msg).to_dict()

            return {
                "status": "success",
                "code": 200,
                "data": filepaths,
            }
        except Exception as exp:
            return ServiceException(500, self._get_user_id(user), str(exp), links=[]).to_dict()
