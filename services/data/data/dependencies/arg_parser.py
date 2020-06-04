""" Argument Parser """

from os import environ
from nameko.extensions import DependencyProvider

# from shapely.geometry.base import geom_from_wkt, WKTReadingError
# from pyproj import Proj, transform
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
