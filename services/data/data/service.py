""" EO Data Discovery """
# TODO: Adding paging with start= maxRecords= parameter for record requesting 

import os
import json
import logging
from typing import Union
from nameko.rpc import rpc

from .schemas import CollectionSchema, CollectionsSchema
from .dependencies.csw import CSWSession
from .dependencies.arg_parser import ArgParserProvider, ValidationError


service_name = "data"
LOGGER = logging.getLogger('standardlog')

class ServiceException(Exception):
    """ServiceException raises if an exception occured while processing the 
    request. The ServiceException is mapping any exception to a serializable
    format for the API gateway.
    """

    def __init__(self, code: int, user_id: str, msg: str,
                 internal: bool=True, links: list=[]):
        self._service = service_name
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


class DataService:
    """Discovery of Earth observation datasets that are available at the back-end.
    """

    name = service_name

    arg_parser = ArgParserProvider()
    csw_session = CSWSession()

    @rpc
    def get_all_products(self, user_id: str=None) -> Union[list, dict]:
        """Requests will ask the back-end for available data and will return an array of 
        available datasets with very basic information such as their unique identifiers.

        Keyword Arguments:
            user_id {str} -- The user id (default: {None})

        Returns:
             Union[list, dict] -- The products or a serialized exception
        """

        try:
            product_records = self.csw_session.get_all_products()
            response = CollectionsSchema().dump(product_records).data

            return {
                "status": "success",
                "code": 200,
                "data": response
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                links=["#tag/EO-Data-Discovery/paths/~1data/get"]).to_dict()

    @rpc
    def get_product_detail(self, user_id: str=None, collection_id: str=None) -> dict:
        """The request will ask the back-end for further details about a dataset.

        Keyword Arguments:
            user_id {str} -- The user id (default: {None})
            name {str} -- The product identifier (default: {None})

        Returns:
            dict -- The product or a serialized exception
        """

        try:
            collection_id = self.arg_parser.parse_product(collection_id)
            product_record = self.csw_session.get_product(collection_id)
            response = CollectionSchema().dump(product_record).data
            
            # Add properties
            json_file = os.path.join(os.path.dirname(__file__), "dependencies", "jsons", collection_id + ".json")
            if json_file:
                properties = json.load(open(json_file))
                response['properties'] = properties
            
            return {
                "status": "success",
                "code": 200,
                "data": response
            }
        except ValidationError as exp:
            return ServiceException(exp.code, user_id, str(exp), internal=False,
                links=["#tag/EO-Data-Discovery/paths/~1collections~1{name}/get"]).to_dict()
        except Exception as exp:
            return ServiceException(500, user_id, str(exp)).to_dict()

    @rpc
    def refresh_cache(self, user_id: str=None, use_cache: bool=False) -> dict:
        """The request will refresh the cache

        Keyword Arguments:
            user_id {str} -- The user id (default: {None})
            use_cache {bool} -- Trigger to refresh the cache

        Returns:
            dict -- Success message or Exception
        """

        try:
            self.csw_session.refresh_cache(use_cache)

            return {
                "status": "success",
                "code": 200,
                "data": {"message": "Successfully refreshed cache"}
            }
        except ValidationError as exp:
            return ServiceException(400, user_id, str(exp), internal=False,
                links=["#tag/EO-Data-Discovery/paths/~1collections~1{name}/get"]).to_dict()
        except Exception as exp:
            return ServiceException(500, user_id, str(exp)).to_dict()
