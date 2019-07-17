""" Schemas """

from marshmallow import Schema, fields

class ExtentSchema(Schema):
    """ Schema for Extent """
    spatial = fields.List(fields.Float(), required=True)
    # temporal = fields.List(fields.String(), allow_none=True)
    temporal = fields.List(fields.String(), required=True, missing=None)
    # temporal = fields.List(fields.DateTime(format='%Y-%m-%dT%H:%M:%S.%f'), required=True, missing='null')

class ProvidersSchema(Schema):
    """ Schema for Provider """
    # Missing items in DB

class PropertiesSchema(Schema):
    """ Schema for Properties """
    # Missing items in DB, should somehow relate to BandSchema

class LinkSchema(Schema):
    """ Schema for Links """
    href = fields.String(required=True)
    rel = fields.String(required=True)
    type = fields.String()
    title = fields.String()

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

    stac_version = fields.String(required=True)
    id = fields.String(required=True)
    description = fields.String(required=True)
    license = fields.String(required=True)
    extent = fields.Nested(ExtentSchema, required=True)
    links = fields.List(fields.Nested(LinkSchema), required=True)
    title = fields.String()
    keywords = fields.List(fields.String())
    providers = fields.Nested(ProvidersSchema)
    version = fields.String() # Missing in DB
    properties = fields.Nested(PropertiesSchema)

# class RecordSchema(Schema):
#     """ Schema for Record """

#     name = fields.String(required=True)
#     path = fields.String(required=True)
#     spatial_extent = fields.Nested(SpatialExtentSchema, required=True)
#     temporal_extent = fields.String()

# class FilePathSchema(Schema):
#     """ Schema for FilePath """

#     date = fields.String(required=True)
#     name = fields.String(required=True)
#     path = fields.String(required=True)

