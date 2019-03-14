''' Argument Parser '''

from nameko.extensions import DependencyProvider
from shapely.geometry.base import geom_from_wkt, WKTReadingError
from pyproj import Proj, transform
from datetime import datetime
from ast import literal_eval

from .aliases import product_aliases


class ValidationError(Exception):
    ''' ValidationError raises if a error occures while validating the arguments. '''

    def __init__(self, msg: str=""):
        super(ValidationError, self).__init__(msg)


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


class BBox:
    """The BBox represents a spatial extention
    """

    @staticmethod
    def get_bbox(qgeom: any) -> object:
        """Returns the parsed Bounding Box object. Input representations can be a lists, dicts or a strings.

        Arguments:
            qgeom {any} -- The input bounding box representation

        Raises:
            ValidationError -- If a error occures while parsing the spatial extent

        Returns:
            BBox -- The bounding box object
        """

        types = {
            dict: lambda x: [x["north"], x["east"], x["south"], x["west"]],
            list: lambda x: [x[0], x[1], x[2], x[3]],
            str: lambda x: list(geom_from_wkt(
                "POLYGON" + x).bounds) if x.startswith("((") else literal_eval(x)
        }

        try:
            # Map the bounding box type
            bounds = types.get(type(qgeom), None)(qgeom)
            if not bounds:
                raise ValidationError(
                    "Type of Polygon/Bbox '{0}' is wrong.".format(qgeom))

            return BBox(bounds[0], bounds[1], bounds[2], bounds[3])
        except WKTReadingError:
            raise ValidationError(
                "Format of Polygon '{0}' is wrong (e.g. '((4 4, -4 4, 4 -4, -4 -4, 4 4))').".format(qgeom))

    def __init__(self, x1: float, y1: float, x2: float, y2: float, epsg: str=None):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.epsg = epsg

    def map_cords(self, out_epsg: str="epsg:4326"):
        """Maps the coordinates between different projections.

        Keyword Arguments:
            out_epsg {str} -- Output projection (default: {"epsg:4326"})
        """

        in_proj = Proj(init=self.epsg)
        out_proj = Proj(init=out_epsg)
        self.x1, self.y1 = transform(in_proj, out_proj, self.x1, self.y1)
        self.x2, self.y2 = transform(in_proj, out_proj, self.x2, self.y2)
        self.epsg = out_epsg


class ArgParser:
    """The ArgParser provides methods for parsing and validating the input data.
    """

    def __init__(self):
        self._prd_map = MultiDict()
        for product in product_aliases:
            self._prd_map.map_keys(product["aliases"], product["product_id"])

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
        product = self._prd_map.get(data_id, None)

        if not product:
            raise ValidationError(
                "Product specifier '{0}' is not valid.".format(data_id))

        return product

    def parse_spatial_extent(self, spatial_extent: str) -> list:
        """Parse the spatial extent

        Arguments:
            spatial_extent {str} -- The spatial extent

        Raises:
            ValidationError -- If a error occures while parsing the spatial extent

        Returns:
            list -- The validated and parsed spatial extent
        """

        if isinstance(spatial_extent, list):
            if not len(spatial_extent) == 4:
                raise ValidationError(
                    "Dimension of Bbox '{0}' is wrong (north, west, south, east).".format(spatial_extent))
        if isinstance(spatial_extent, str):
            if not (spatial_extent.startswith("((") or spatial_extent.startswith("[")):
                raise ValidationError(
                    "Format of Polygon '{0}' is wrong (e.g. '((4 4, -4 4, 4 -4, -4 -4, 4 4))').".format(spatial_extent))

        bbox = BBox.get_bbox(spatial_extent)
        if "crs" in spatial_extent:
            bbox.epsg = spatial_extent["crs"]

        return bbox

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

            start = datetime.strptime(temporal_extent["from"], '%Y-%m-%d')
            end = datetime.strptime(temporal_extent["to"], '%Y-%m-%d')

            if end < start:
                raise ValidationError("End date is before start date.")

            return temporal_extent["from"] + "T00:00:00Z", temporal_extent["to"] + "T23:59:59Z"
        except ValueError:
            raise ValidationError(
                "Format of start date '{0}' is wrong.".format(start))


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

        return ArgParser()
