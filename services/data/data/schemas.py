"""Provides all schemas definitions used in the main service to serialize and deserialize data.

Schemas are defined to fit request return schemas defined in the `OpenEO API EO Data Discovery`_
"""
from typing import Any, List

from marshmallow import Schema, fields, post_dump


class BaseSchema(Schema):
    """Base Schema including functionality useful in all other schemas."""

    __skip_values__: List[Any] = [None, []]
    """Key value pairs where the value is one of these will not be dumped.

    There is no need to return unset keys and overload returned dictionaries with 'meaningless' key value pairs.
    """
    __return_anyway__: List[str] = []
    """These keys will always be returned, also if their value is in __skip_values__.

    Therefore __return_anyway__ overwrites __skip_values__. This is useful if a return key is required by the
    `OpenEO API`_ but it's value may be in __skip_values__.
    """

    @post_dump
    def remove_skip_values(self, data: dict, **kwargs: Any) -> dict:
        """Remove keys where value is in __skip_values__ but key is not in __return_anyway__."""
        return {
            key: value for key, value in data.items()
            if value not in self.__skip_values__ or key in self.__return_anyway__
        }


class SpatialExtentSchema(BaseSchema):
    """Schema for spatial extent."""

    bbox = fields.List(fields.List(fields.Float()), required=True)


class TemporalExtentSchema(BaseSchema):
    """Schema for temporal extent."""

    interval = fields.List(fields.List(fields.String()), required=True)


class ExtentSchema(BaseSchema):
    """Schema for extent holding both spatial and temporal extend."""

    spatial = fields.Nested(SpatialExtentSchema, required=True)
    temporal = fields.Nested(TemporalExtentSchema, required=True)


class ProvidersSchema(BaseSchema):
    """Schema for Provider.

    Currently not implemented - content is missing in DB.
    """

    # TODO Missing items in DB


class LinkSchema(BaseSchema):
    """Schema for Links."""

    href = fields.String(required=True)
    rel = fields.String(required=True)
    type_ = fields.String(data_key="type")
    title = fields.String()


class BandSchema(BaseSchema):
    """Schema for band."""

    band_id = fields.String(required=True)
    offset = fields.Integer(required=True)
    res_m = fields.Integer(required=True)
    scale = fields.Float(required=True)
    type_ = fields.String(data_key="type", required=True)
    unit = fields.String(required=True)
    wavelength_nm = fields.Float(required=True)


class CollectionSchema(BaseSchema):
    """Schema for single collection."""

    stac_version = fields.String(required=True)
    id_ = fields.String(data_key="id", required=True)
    title = fields.String()
    description = fields.String(required=True)
    keywords = fields.List(fields.String())
    version = fields.String()  # Missing in DB
    license_ = fields.String(data_key="license", required=True)
    providers = fields.Nested(ProvidersSchema)
    extent = fields.Nested(ExtentSchema, required=True)
    links = fields.List(fields.Nested(LinkSchema), required=True)


class CollectionsSchema(BaseSchema):
    """Schema for set of collections."""

    __return_anyway__ = ["links"]

    collections = fields.List(
        fields.Nested(CollectionSchema()),
        required=True,
    )
    links = fields.List(fields.Nested(LinkSchema), required=True)
