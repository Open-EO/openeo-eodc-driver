""" Schemas """

from marshmallow import Schema, fields

class ExtentSchema(Schema):
    """ Schema for Extent """
    spatial = fields.List(fields.Float(), required=True)
    temporal = fields.List(fields.String(), required=True, missing=None)

class ProvidersSchema(Schema):
    """ Schema for Provider """
    # TODO Missing items in DB

class PropertiesSchema(Schema):
    """ Schema for Properties """
    # TODO Missing items in DB, should somehow relate to BandSchema

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

class OtherPropertiesSchema(Schema):
    """ Schema for Other Properties """
    # TODO Missing items in DB

class CollectionSchema(Schema):
    """ Schema for Collection """

    stac_version = fields.String(required=True)
    id = fields.String(required=True)
    title = fields.String()
    description = fields.String(required=True)
    keywords = fields.List(fields.String())
    version = fields.String() # Missing in DB
    license = fields.String(required=True)
    providers = fields.Nested(ProvidersSchema)
    extent = fields.Nested(ExtentSchema, required=True)
    links = fields.List(fields.Nested(LinkSchema), required=True)
    other_properties = fields.Nested(OtherPropertiesSchema, required=True, default={})
    properties = fields.Nested(PropertiesSchema, required=True, default={})

class CollectionsSchema(Schema):
    """ Schema for Collections """

    collections = fields.List(fields.Nested(CollectionSchema(exclude=['properties', 'other_properties'])), required=True)
    links = fields.List(fields.Nested(LinkSchema), required=True)
