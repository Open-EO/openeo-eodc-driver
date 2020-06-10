""" Schemas """
from typing import Any, List

from marshmallow import Schema, fields, post_dump


class BaseSchema(Schema):
    __skip_values__: List[Any] = [None, []]
    __return_anyway__: List[str] = []

    @post_dump
    def remove_skip_values(self, data: dict, **kwargs: Any) -> dict:
        return {
            key: value for key, value in data.items()
            if value not in self.__skip_values__ or key in self.__return_anyway__
        }


class ExtentSchema(BaseSchema):
    """ Schema for Extent """

    spatial = fields.List(fields.Float(), required=True)
    temporal = fields.List(fields.String(), required=True)


class ProvidersSchema(BaseSchema):
    """ Schema for Provider """

    # TODO Missing items in DB


class LinkSchema(BaseSchema):
    """ Schema for Links """

    href = fields.String(required=True)
    rel = fields.String(required=True)
    type = fields.String()
    title = fields.String()


class BandSchema(BaseSchema):
    """ Schema for Band """

    band_id = fields.String(required=True)
    offset = fields.Integer(required=True)
    res_m = fields.Integer(required=True)
    scale = fields.Float(required=True)
    type = fields.String(required=True)
    unit = fields.String(required=True)
    wavelength_nm = fields.Float(required=True)


class CollectionSchema(BaseSchema):
    """ Schema for Collection """

    stac_version = fields.String(required=True)
    id = fields.String(required=True)
    title = fields.String()
    description = fields.String(required=True)
    keywords = fields.List(fields.String())
    version = fields.String()  # Missing in DB
    license = fields.String(required=True)
    providers = fields.Nested(ProvidersSchema)
    extent = fields.Nested(ExtentSchema, required=True)
    links = fields.List(fields.Nested(LinkSchema), required=True)


class CollectionsSchema(BaseSchema):
    """ Schema for Collections """
    __return_anyway__ = ["links"]

    collections = fields.List(
        fields.Nested(CollectionSchema()),
        required=True,
    )
    links = fields.List(fields.Nested(LinkSchema), required=True)
