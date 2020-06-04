""" Argument Parser """

from os import environ
from nameko.extensions import DependencyProvider

# from shapely.geometry.base import geom_from_wkt, WKTReadingError
# from pyproj import Proj, transform
from datetime import datetime
from ast import literal_eval
import logging

from .aliases import product_aliases
from .cache import get_cache_path, get_json_cache

LOGGER = logging.getLogger("standardlog")


class ValidationError(Exception):
    """ ValidationError raises if a error occures while validating the arguments. """

    def __init__(self, msg: str = "", code: int = 400):
        super(ValidationError, self).__init__(msg)
        self.code = code


class MultiDict(dict):
    """The MultiDict is an extention to the Python dict, providing the
    mapping of multiple keys to the same value.
    """

    def map_keys(self, keys: list, value: any):
        """Maps the keys to the same value.

        Arguments:
            keys {list} -- List of keys
            value {any} -- The value, to which the keys should point
        """

        for key in keys:
            self[key] = value


class ArgParser:
    """The ArgParser provides methods for parsing and validating the input data.
    """

    def __init__(self, cache_path: str):
        # self._prd_map = MultiDict()
        # for product in product_aliases:
        #     self._prd_map.map_keys(product["aliases"], product["product_id"])
        self.cache_path = cache_path

    def parse_product(self, data_id: str) -> str:
        """Parse the product identifier

        Arguments:
            data_id {str} -- The product identifier

        Raises:
            ValidationError -- If a error occures while parsing the spatial extent

        Returns:
            str -- The validated and product identifier
        """

        data_id = data_id.lower().replace(" ", "")
        # product = self._prd_map.get(data_id, None)
        cache_path = get_cache_path(self.cache_path, data_id)
        product = get_json_cache(cache_path)

        if not product:

            raise ValidationError("Collection '{0}' not found.".format(data_id), 404)

        return data_id

    def parse_temporal_extent(self, temporal_extent: str) -> str:
        """Parse the temporal extent

        Arguments:
            temporal_extent {str} -- The temporal extent

        Raises:
            ValidationError -- If a error occures while parsing the temporal extent

        Returns:
            str -- The validated and parsed start and end dates
        """

        try:
            if isinstance(temporal_extent, str):
                temp_split = temporal_extent.split("/")
                temporal_extent = {"from": temp_split[0], "to": temp_split[1]}

            start = datetime.strptime(temporal_extent["from"], "%Y-%m-%d")
            end = datetime.strptime(temporal_extent["to"], "%Y-%m-%d")

            if end < start:
                raise ValidationError("End date is before start date.")

            return (
                temporal_extent["from"] + "T00:00:00Z",
                temporal_extent["to"] + "T23:59:59Z",
            )
        except ValueError:
            raise ValidationError("Format of start date '{0}' is wrong.".format(start))


class ArgParserProvider(DependencyProvider):
    """The ArgParserProvider is the DependencyProvider of the ArgParser.
    """

    def get_dependency(self, worker_ctx: object) -> ArgParser:
        """Return the instantiated object that is injected to a
        service worker

        Arguments:
            worker_ctx {object} -- The worker object

        Returns:
            ArgParser -- he instantiated ArgParser object
        """

        return ArgParser(environ.get("CACHE_PATH"))
