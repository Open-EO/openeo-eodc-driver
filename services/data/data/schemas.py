""" Schemas """

from marshmallow import Schema, fields


class SpatialExtentSchema(Schema):
    """ Schema for SpatialExtent """

    top = fields.Float(required=True)
    bottom = fields.Float(required=True)
    left = fields.Float(required=True)
    right = fields.Float(required=True)
    crs = fields.String(required=True)


class BandSchema(Schema):
    """ Schema for Band """

    band_id = fields.String(required=True)
    offset = fields.Integer(required=True)
    res_m = fields.Integer(required=True)
    scale = fields.Float(required=True)
    type = fields.String(required=True)
    unit = fields.String(required=True)
    wavelength_nm = fields.Float(required=True)


class ProductRecordSchema(Schema):
    """ Schema for ProductRecord """

    description = fields.String(required=True)
    data_id = fields.String(required=True)
    source = fields.String(required=True)
    spatial_extent = fields.Nested(SpatialExtentSchema)
    temporal_extent = fields.String()
    bands = fields.Nested(BandSchema, many=True)

class RecordSchema(Schema):
    """ Schema for ProductRecord """

    name = fields.String(required=True)
    path = fields.String(required=True)
    spatial_extent = fields.Nested(SpatialExtentSchema, required=True)
    temporal_extent = fields.String()

class FilePathSchema(Schema):
    """ Schema for FilePath """

    date = fields.String(required=True)
    name = fields.String(required=True)
    path = fields.String(required=True)