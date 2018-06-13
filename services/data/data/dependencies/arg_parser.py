''' Argument Parser '''

from nameko.extensions import DependencyProvider
from shapely.geometry.base import geom_from_wkt, WKTReadingError
from pyproj import Proj, transform
from datetime import datetime
from ast import literal_eval
from .products import products
from ..exceptions import ValidationError
import ast

class MultiDict(dict):
    def map_keys(self, keys, value):
        for key in keys:
            self[key] = value


class BBox:
    @staticmethod
    def get_bbox(qgeom):
        types = {
            dict: lambda x: [x["top"], x["right"], x["bottom"], x["left"]],
            list: lambda x: [x[0], x[1], x[2], x[3]],
            str:  lambda x: list(geom_from_wkt("POLYGON" + x).bounds) if x.startswith("((") else literal_eval(x)
        }

        try:
            bounds = types.get(type(qgeom), None)(qgeom)
            if not bounds:
                raise ValidationError("Type of Polygon/Bbox '{0}' is wrong.".format(qgeom))

            return BBox(bounds[0], bounds[1], bounds[2], bounds[3])
        except WKTReadingError:
            raise ValidationError("Format of Polygon '{0}' is wrong (e.g. '((4 4, -4 4, 4 -4, -4 -4, 4 4))').".format(qgeom))

    def __init__(self, x1, y1, x2, y2, epsg=None):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.epsg = epsg

    def map_cords(self, out_epsg="epsg:4326"):
        in_proj = Proj(init=self.epsg)
        out_proj = Proj(init=out_epsg)
        self.x1, self.y1 = transform(in_proj, out_proj, self.x1, self.y1)
        self.x2, self.y2 = transform(in_proj, out_proj, self.x2, self.y2)
        self.epsg = out_epsg


class ArgValidator:
    def __init__(self):
        self._prd_map = MultiDict()
        for product in products:
            self._prd_map.map_keys(product["aliases"], product["product_id"])

    def parse(self, product, bbox, start, end):
        """ Parses the input arguments """

        product = self.parse_product(product) if product else None
        bbox = self.parse_bbox(bbox) if bbox else None
        start = self.parse_start(start) if start else None
        end = self.parse_end(end) if end else None

        return product, bbox, start, end

    def parse_product(self, qname):
        qname = qname.lower().replace(" ", "")
        product = self._prd_map.get(qname, None)

        if not product:
            raise ValidationError("Product specifier '{0}' is not valid.".format(qname))

        return product

    def parse_bbox(self, qgeom):
        if isinstance(qgeom, list):
            if not len(qgeom) == 4:
                raise ValidationError("Dimension of Bbox '{0}' is wrong (north, west, south, east).".format(qgeom))
        if isinstance(qgeom, str):
            if not (qgeom.startswith("((") or qgeom.startswith("[")):
                raise ValidationError("Format of Polygon '{0}' is wrong (e.g. '((4 4, -4 4, 4 -4, -4 -4, 4 4))').".format(qgeom))

        bbox = BBox.get_bbox(qgeom)
        if "srs" in qgeom:
            bbox.epsg = qgeom["srs"]

        return bbox

    def parse_start(self, start):
        try:
            datetime.strptime(start, '%Y-%m-%d')
            return start + "T00:00:00Z"
        except ValueError:
            raise ValidationError("Format of start date '{0}' is wrong.".format(start))
    
    def parse_end(self, end):
        try:
            datetime.strptime(end, '%Y-%m-%d')
            return end + "T23:59:59Z"
        except ValueError:
            raise ValidationError("Format of end date '{0}' is wrong.".format(end))


class ArgValidatorProvider(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return ArgValidator()
