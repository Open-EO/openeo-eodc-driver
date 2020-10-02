""" EO Data Discovery """

import logging
from pprint import pformat
from typing import Any, Dict, List, Optional, Union

from dynaconf import settings
from nameko.rpc import rpc

from .dependencies.arg_parser import ValidationError
from .dependencies.csw import CSWSession, CSWSessionDC
from .dependencies.settings import initialise_settings
from .dependencies.wekeo_hda import HDASession
from .models import Collections
from .schema import CollectionSchema, CollectionsSchema

service_name = "data"
LOGGER = logging.getLogger("standardlog")
initialise_settings()


class ServiceException(Exception):
    """ServiceException raises if an exception occured while processing the
    request. The ServiceException is mapping any exception to a serializable
    format for the API gateway.
    """

    def __init__(
            self, code: int, user_id: Optional[str], msg: str, internal: bool = True, links: list = None
    ) -> None:
        self._service = service_name
        self._code = code
        self._user_id = user_id if user_id else "None"
        self._msg = msg
        self._internal = internal
        self._links = links if links else []
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
            "links": self._links,
        }


class DataService:
    """Discovery of Earth observation datasets that are available at the back-end.
    """

    name = service_name
    if settings.IS_CSW_SERVER:
        csw_session = CSWSession()
    if settings.IS_CSW_SERVER_DC:
        csw_session_dc = CSWSessionDC()
    if settings.IS_HDA_WEKEO:
        hda_session = HDASession()

    def __init__(self) -> None:
        LOGGER.info(f"Initialized {self}")

    def __repr__(self) -> str:
        return f"DataService('{self.name}')"

    @rpc
    def get_all_products(self, user: Dict[str, Any] = None) -> Union[list, dict]:
        """Requests will ask the back-end for available data and will return an array of
        available datasets with very basic information such as their unique identifiers.

        Keyword Arguments:
            user {Dict[str, Any]} -- The user (default: {None})

        Returns:
             Union[list, dict] -- The products or a serialized exception
        """

        LOGGER.info("All products requested")
        LOGGER.debug("user_id requesting %s", self.get_user_id(user))
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
                self.get_user_id(user),
                str(exp),
                links=["#tag/EO-Data-Discovery/paths/~1data/get"],
            ).to_dict()

    @rpc
    def get_product_detail(
            self, collection_id: str, user: Dict[str, Any] = None
    ) -> dict:
        """The request will ask the back-end for further details about a dataset.

        Keyword Arguments:
            user {Dict[str, Any]} -- The user (default: {None})
            name {str} -- The product identifier (default: {None})

        Returns:
            dict -- The product or a serialized exception
        """

        try:
            LOGGER.info("%s product requested", collection_id)

            if settings.IS_CSW_SERVER and collection_id in settings.WHITELIST:
                product_record = self.csw_session.get_product(collection_id)
            elif settings.IS_CSW_SERVER_DC and collection_id in settings.WHITELIST_DC:
                product_record = self.csw_session_dc.get_product(collection_id)
            elif settings.IS_HDA_WEKEO and collection_id in settings.WHITELIST_WEKEO:
                product_record = self.hda_session.get_product(collection_id)

            # Check user permission
            # TODO: implement better logc for checking user permissions
            error_code = None
            if collection_id in ('TUW_SIG0_S1') and not user:
                error_code = 401  # Unauthorized
                error_msg = "This collection is not publicly accessible."
            elif collection_id in ('TUW_SIG0_S1') and \
                    user and self.csw_session_dc.data_access not in user["profile"]["data_access"]:
                error_code = 403  # Forbidden (dpes not have permissions)
                error_msg = "User is not authorized to access this collection."
            if error_code:
                return ServiceException(
                    error_code,
                    self.get_user_id(user),
                    error_msg,
                    internal=False,
                    links=[],
                ).to_dict()

            response = CollectionSchema().dump(product_record)

            LOGGER.debug("response:\n%s", pformat(response))
            return {"status": "success", "code": 200, "data": response}
        except ValidationError as exp:
            return ServiceException(
                exp.code,
                self.get_user_id(user),
                str(exp),
                internal=False,
                links=[
                    "#tag/EO-Data-Discovery/paths/~1collections~1{name}/get"],
            ).to_dict()
        except Exception as exp:
            return ServiceException(500, self.get_user_id(user), str(exp)).to_dict()

    @rpc
    def refresh_cache(self, user: Dict[str, Any] = None, use_cache: bool = False) -> dict:
        """The request will refresh the cache

        Keyword Arguments:
            user {Dict[str, Any]} -- The user (default: {None})
            use_cache {bool} -- Trigger to refresh the cache

        Returns:
            dict -- Success message or Exception
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
        except ValidationError as exp:
            return ServiceException(
                400,
                self.get_user_id(user),
                str(exp),
                internal=False,
                links=[
                    "#tag/EO-Data-Discovery/paths/~1collections~1{name}/get"],
            ).to_dict()
        except Exception as exp:
            return ServiceException(500, self.get_user_id(user), str(exp)).to_dict()

    def get_user_id(self, user: Optional[Dict[str, Any]]) -> Optional[str]:
        return user["id"] if user and "id" in user else None

    @rpc
    def get_filepaths(self, collection_id: str, spatial_extent: List[float], temporal_extent: List[str],
                      user: Dict[str, Any] = None) -> Dict:
        """The request will return a list of filepaths.

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
                return ServiceException(500, self.get_user_id(user), msg=msg).to_dict()

            return {
                "status": "success",
                "code": 200,
                "data": filepaths,
            }
        except Exception as exp:
            return ServiceException(500, self.get_user_id(user), str(exp), links=[]).to_dict()
