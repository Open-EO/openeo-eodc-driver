"""Provides all schemas definitions used in the main service to serialize and deserialize data.

Schemas are defined to fit request return schemas defined in the `OpenEO API Batch Jobs`_.

_OpenEO API Batch Jobs: https://open-eo.github.io/openeo-api/#tag/Batch-Jobs
"""
from typing import Any, Dict, List, Optional
from uuid import uuid4

from marshmallow import Schema, fields, post_dump, post_load, pre_load

from .models import Base, Job


class BaseSchema(Schema):
    """Base Schema including functionality useful in all other schemas."""

    __skip_values__: list = [None, []]
    """Key value pairs where the value is one of these will not be dumped.

    There is no need to return unset keys and overload returned dictionaries with 'meaningless' key value pairs.
    """
    __model__: Base = None
    """Database model table class."""

    @post_dump
    def remove_skip_values(self, data: dict, **kwargs: Any) -> dict:
        """Remove keys where value is in __skip_values__."""
        return {
            key: value for key, value in data.items()
            if value not in self.__skip_values__
        }

    @post_load
    def make_object(self, data: dict, **kwargs: Any) -> Base:
        """Create a database object from a deserialized object."""
        if self.__model__:
            return self.__model__(**data)


class MoneyConverter:
    """Convert between euro and cent.

    Used to convert different fields when serializing and deserializing. As different parameters are passed depending on
    whether a VALUE is deserialized or an OBJECT is deserialized different method are required.
    """

    def to_cent(self, obj: Optional[float]) -> Optional[int]:
        """Convert an amount in euro to cent."""
        if obj:
            return int(obj * 100)
        return None

    def to_euro_budget(self, obj: Job) -> Optional[float]:
        """Convert the 'budget' from cent to euro."""
        if obj.budget:
            return obj.budget / 100.0
        return None

    def to_euro_cost(self, obj: Job) -> Optional[float]:
        """Convert the 'current_costs' from cent to euro."""
        if obj.current_costs:
            return obj.current_costs / 100.0
        return None


class NestedDict(fields.Nested):
    """Allow nesting a schema inside a dictionary.

    This is analogous to nesting a schema inside a list but using a dictionary with a given key instead.

    Attributes:
        nested: The nested schema.
        key: The key in the serialized dictionary which value holds the key name of the deserialized object.
            E.g. key='foo'
            input: [{'a': '1', 'b': 2, 'foo': 'bar'}, {... 'foo': 'baz'}]
            -> serialize
            -> {'bar': {'a': '1', 'b': 2}, 'baz': {...}}
            (assuming the schema matches)
        kwargs: The same keyword arguments that :class:`Field` receives.
    """

    def __init__(self, nested: Any, key: str, **kwargs: dict) -> None:
        """Initialize nested dictionary field."""
        super().__init__(nested, many=True, **kwargs)
        self.key = key

    def _serialize(self, nested_obj: List[Any], attr: str, obj: Any, **kwargs: dict) -> Dict[str, Any]:
        """Convert a list nested dictionaries to a dictionary of dictionaries using the ."""
        nested_list = super()._serialize(nested_obj, attr, obj)
        nested_dict = {item.pop(self.key): item for item in nested_list}
        return nested_dict

    def _deserialize(self, value: Dict[str, Any], attr: str, data: Any, **kwargs: dict) -> List[Any]:
        """Convert a dictionary of dictionaries to a list of dictionaries."""
        raw_list = []
        for key, item in value.items():
            item[self.key] = key
            raw_list.append(item)
        nested_list = super()._deserialize(raw_list, attr, data)
        return nested_list


class JobShortSchema(BaseSchema, MoneyConverter):
    """Schema including general information of a job."""
    id = fields.String(required=True)
    title = fields.String()
    description = fields.String()
    status = fields.String(required=True)
    created = fields.DateTime(attribute="created_at", required=True)
    # database is updated on REST call does not correspond to when the status changed on airflow
    # updated = fields.DateTime(attribute="status_updated_at")
    plan = fields.String()
    costs = fields.Method('to_euro_cost', deserialize='to_cent', attribute="current_costs")
    budget = fields.Method('to_euro_budget', deserialize='to_cent')


class JobFullSchema(JobShortSchema):
    """Schema including detailed information about a job."""
    process = fields.Dict(required=True)
    progress = fields.Float()


class JobCreateSchema(BaseSchema, MoneyConverter):
    """Schema to create a database job object from job_args provided by the user."""

    __model__ = Job
    """The database table model to convert the data to."""

    id = fields.String(required=True)
    user_id = fields.String(required=True)
    title = fields.String()
    description = fields.String()
    process_graph_id = fields.String(required=True)
    plan = fields.String()
    budget = fields.Method('to_euro_budget', deserialize='to_cent')

    @pre_load
    def add_job_id(self, in_data: dict, **kwargs: Any) -> dict:
        """Generate random uuid and add it as job identifier."""
        in_data['id'] = 'jb-' + str(uuid4())
        return in_data


class ProviderSchema(BaseSchema):
    """Schema to store provider information."""
    name = fields.String(required=True)
    description = fields.String()
    role = fields.String()  # enum
    url = fields.Url()


class PropertiesSchema(BaseSchema):
    """Schema to store result properties."""

    DEFINED_KEYS = ["datetime", "start_datetime", "end_datetime", "title", "description", "license", "providers",
                    "created", "updated", "expires"]
    """List of all defined key in this schema. Any other information will be stored in the container key 'additional'.
    """

    datetime = fields.DateTime(required=True)
    start_datetime = fields.DateTime()
    end_datetime = fields.DateTime()
    title = fields.String()
    description = fields.String()
    license = fields.String()  # Stac license
    providers = fields.List(fields.Nested(ProviderSchema))
    created = fields.DateTime()
    updated = fields.DateTime()
    expires = fields.DateTime()
    additional = fields.Dict()

    @pre_load
    def separate_additional_keys(self, in_data: dict, **kwargs: dict) -> dict:
        """Add any additional key value pairs to the 'additional' key."""
        additional_keys = [key for key in in_data.keys() if key not in self.DEFINED_KEYS]
        in_data['additional'] = {key: in_data.pop(key) for key in additional_keys}
        return in_data

    @post_dump
    def add_additional_keys(self, data: dict, **kwargs: dict) -> dict:
        """Add all key value pairs stored in the additional key back to the main level of the dictionary."""
        data.update(data.pop('additional'))
        if 'additional' in data.keys():
            data.pop('additional')
        return data


class AssetSchema(BaseSchema):
    """Schema to store information about an asset."""
    href = fields.Url(required=True)
    title = fields.String()
    description = fields.String()
    type = fields.String()
    roles = fields.List(fields.String())
    name = fields.String(required=True)  # Asset's dict key


class LinkSchema(BaseSchema):
    """Schema to store details about a link."""
    rel = fields.String(required=True)
    href = fields.Url(required=True)
    type = fields.String()
    title = fields.String()


class GeometrySchema(BaseSchema):
    """Schema to store geometry - currently only raw coordinates are supported."""
    type = fields.String(required=True)  # enum
    coordinates = fields.Raw(required=True)
    # we don't support GeoJson GeometryCollection


class JobResultsBaseSchema(BaseSchema):
    """Base schema for job results."""
    id = fields.String(required=True)
    title = fields.String(required=False)
    description = fields.String(required=False)
    status = fields.String(required=True)
    assets = NestedDict(key="name", nested=AssetSchema)
    stac_version = fields.String(required=True)
    stac_extension = fields.List(fields.String())  # string or url
    links = fields.List(fields.Nested(LinkSchema), required=True)


class JobResultsMetadataSchema(BaseSchema):
    """Schema for results' metadata."""
    type = fields.String(required=True)
    bbox = fields.List(fields.Float(), required=True)
    geometry = fields.Nested(GeometrySchema, required=True)
    properties = fields.Nested(PropertiesSchema, required=True)
