""" EO Data Discovery """
# TODO: Adding paging with start= maxRecords= parameter for record requesting 

from typing import Union
from nameko.rpc import rpc

from .schemas import ProductRecordSchema
from .dependencies.csw import CSWSession
from .dependencies.arg_parser import ArgParserProvider, ValidationError


service_name = "data"


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
            response = ProductRecordSchema(many=True).dump(product_records).data

            return {
                "status": "success",
                "code": 200,
                "data": response
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                links=["#tag/EO-Data-Discovery/paths/~1data/get"]).to_dict()

    @rpc
    def get_product_detail(self, user_id: str=None, name: str=None) -> dict:
        """The request will ask the back-end for further details about a dataset.

        Keyword Arguments:
            user_id {str} -- The user id (default: {None})
            name {str} -- The product identifier (default: {None})

        Returns:
            dict -- The product or a serialized exception
        """

        try:
            name = self.arg_parser.parse_product(name)
            product_record = self.csw_session.get_product(name)
            # response = ProductRecordSchema().dump(product_record)
            response = product_record
            return {
                "status": "success",
                "code": 200,
                "data": response
            }
        except ValidationError as exp:
            return ServiceException(400, user_id, str(exp), internal=False,
                links=["#tag/EO-Data-Discovery/paths/~1collections~1{name}/get"]).to_dict()
        except Exception as exp:
            return ServiceException(500, user_id, str(exp)).to_dict()

