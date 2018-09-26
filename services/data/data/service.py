""" EO Data Discovery """
# TODO: Adding paging with start= maxRecords= parameter for record requesting 

from nameko.rpc import rpc
from datetime import datetime
from typing import Union

from .schemas import ProductRecordSchema, RecordSchema, FilePathSchema
from .dependencies.csw import CSWSession, CWSError
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
            response = ProductRecordSchema(many=True).dump(product_records)

            return {
                "status": "success",
                "code": 200,
                "data": response.data
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
            response = ProductRecordSchema().dump(product_record).data

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

    @rpc
    def get_records(self, user_id: str=None, name: str=None, detail: str="full", 
                    spatial_extent: str=None, temporal_extent: str=None) -> Union[list, dict]:
        """The request will ask the back-end for further details about the records of a dataset.
        The records must be filtered by time and space. Different levels of detail can be returned.

        Keyword Arguments:
            user_id {str} -- The user id (default: {None})
            detail {str} -- The detail level (full, short, file_paths) (default: {"full"})
            name {str} -- The product identifier (default: {None})
            spatial_extent {str} -- The spatial extent (default: {None})
            temporal_extent {str} -- The temporal extent (default: {None})

        Returns:
             Union[list, dict] -- The records or a serialized exception
        """
        # TODO: Filter by license -> see process get_data

        try:
            name = self.arg_parser.parse_product(name)

            # Parse the argeuments
            if spatial_extent:
                spatial_extent = self.arg_parser.parse_spatial_extent(spatial_extent)
            if temporal_extent:
                start, end = self.arg_parser.parse_temporal_extent(temporal_extent)
            else:
                start = None
                end = None

            # Retrieve records, based on detail level, and serialize
            response = []
            if detail == "full":
                response = self.csw_session.get_records_full(
                    name, spatial_extent, start, end)
            elif detail == "short":
                records = self.csw_session.get_records_shorts(
                    name, spatial_extent, start, end)
                response = RecordSchema(many=True).dump(records).data
            elif detail == "file_path":
                file_paths = self.csw_session.get_file_paths(
                    name, spatial_extent, start, end)
                response = FilePathSchema(many=True).dump(file_paths).data

            return {
                "status": "success",
                "code": 200,
                "data": response
            }
        except ValidationError as exp:
            return ServiceException(400, user_id, str(exp), internal=False,
                links=["#tag/EO-Data-Discovery/paths/~1data~1{name}~1records/get"]).to_dict()
        except Exception as exp:
            return ServiceException(500, user_id, str(exp)).to_dict()
