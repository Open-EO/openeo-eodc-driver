""" Schemas """
from typing import Any, Dict, List

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


class NestedDict(fields.Nested):
    """
    Allows nesting a schema inside a dictionary.
    This is analogous to nesting schema inside lists but using a dictionary with a given key instead.
    """

    def __init__(self, nested: Any, key: str, *args: set, **kwargs: dict) -> None:
        """
        Initialize nested dictionary field.
        """
        super().__init__(nested, many=True, *args, **kwargs)
        self.key = key

    def _serialize(self, nested_obj: List[Any], attr: str, obj: Any, **kwargs: dict) \
            -> Dict[str, Any]:
        nested_list = super()._serialize(nested_obj, attr, obj)
        nested_dict = {item.pop(self.key): item for item in nested_list}
        return nested_dict

    def _deserialize(self, value: Dict[str, Any], attr: str, data: Any, **kwargs: dict) \
            -> List[Any]:
        raw_list = []
        for key, item in value.items():
            item[self.key] = key
            raw_list.append(item)
        nested_list = super()._deserialize(raw_list, attr, data)
        return nested_list


class SpatialExtentSchema(BaseSchema):
    """ Schema for spatial Extent """

    bbox = fields.List(fields.List(fields.Float()), required=True)


class TemporalExtentSchema(BaseSchema):
    """ Schema for temporal Extent """

    interval = fields.List(fields.List(fields.String()))


class ExtentSchema(BaseSchema):
    """ Schema for Extent """

    spatial = fields.Nested(SpatialExtentSchema, required=True)
    temporal = fields.Nested(TemporalExtentSchema)


class ProvidersSchema(BaseSchema):
    """ Schema for Provider """

    # TODO Missing items in DB

    name = fields.String(required=True)
    description = fields.String()
    roles = fields.List(fields.String)  # TODO ENUM?
    url = fields.Url()


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


class AssetSchema(BaseSchema):
    href = fields.Url(required=True)
    title = fields.String()
    description = fields.String()
    type = fields.String()
    roles = fields.List(fields.String())
    name = fields.String(required=True)  # Asset's dict key


class CollectionSchema(BaseSchema):
    """ Schema for Collection """

    # cube:dimensions and summaries are added separately!

    stac_version = fields.String(required=True)
    stac_extnsion = fields.List(fields.String())
    id = fields.String(required=True)
    title = fields.String()
    description = fields.String(required=True)
    keywords = fields.List(fields.String())
    version = fields.String()  # Missing in DB
    deprecated = fields.Boolean(default=False)
    license = fields.String(required=True)
    providers = fields.Nested(ProvidersSchema)  # TODO List many=True ?
    extent = fields.Nested(ExtentSchema, required=True)
    links = fields.List(fields.Nested(LinkSchema), required=True)
    cube_dimensions = fields.Dict(data_key="cube:dimensions", required=True)
    summaries = fields.Dict(required=True)
    assets = fields.Dict()  # Added for completeness - not filled from our csw!


class CollectionsSchema(BaseSchema):
    """ Schema for Collections """
    __return_anyway__ = ["links"]

    collections = fields.List(
        fields.Nested(CollectionSchema()),
        required=True,
    )
    links = fields.List(fields.Nested(LinkSchema), required=True)