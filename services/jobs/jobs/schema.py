from typing import Any, Dict, List, Optional
from uuid import uuid4

from marshmallow import Schema, fields, post_dump, post_load, pre_load

from .models import Base, Job


class BaseSchema(Schema):
    __skip_values__: list = [None, []]
    __model__: Base = None

    @post_dump
    def remove_skip_values(self, data: dict, **kwargs: Any) -> dict:
        return {
            key: value for key, value in data.items()
            if value not in self.__skip_values__
        }

    @post_load
    def make_object(self, data: dict, **kwargs: Any) -> Base:
        if self.__model__:
            return self.__model__(**data)


class MoneyConverter:
    def to_cent(self, obj: float) -> Optional[int]:
        if obj:
            return int(obj * 100)
        return None

    def to_euro_budget(self, obj: Job) -> Optional[float]:
        if obj.budget:
            return obj.budget / 100.0
        return None

    def to_euro_cost(self, obj: Job) -> Optional[float]:
        if obj.current_costs:
            return obj.current_costs / 100.0
        return None


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


class JobShortSchema(BaseSchema, MoneyConverter):
    id = fields.String(required=True)
    title = fields.String()
    description = fields.String()
    status = fields.String(required=True)
    created = fields.DateTime(attribute="created_at", required=True, format='%Y-%m-%dT%H:%M:%SZ')
    # database is updated on REST call does not correspond to when the status changed on airflow
    # updated = fields.DateTime(attribute="status_updated_at")
    plan = fields.String()
    costs = fields.Method('to_euro_cost', deserialize='to_cent', attribute="current_costs")
    budget = fields.Method('to_euro_budget', deserialize='to_cent')


class JobFullSchema(JobShortSchema):
    process = fields.Dict(required=True)
    progress = fields.Float()


class JobCreateSchema(BaseSchema, MoneyConverter):
    __model__ = Job

    id = fields.String(required=True)
    user_id = fields.String(required=True)
    title = fields.String()
    description = fields.String()
    process_graph_id = fields.String(required=True)
    plan = fields.String()
    budget = fields.Method('to_euro_budget', deserialize='to_cent')

    @pre_load
    def add_process_graph_id(self, in_data: dict, **kwargs: Any) -> dict:
        in_data['id'] = 'jb-' + str(uuid4())
        return in_data


class ProviderSchema(BaseSchema):
    name = fields.String(required=True)
    description = fields.String()
    role = fields.String()  # enum
    url = fields.Url()


class PropertiesSchema(BaseSchema):
    DEFINED_KEYS = ["datetime", "start_datetime", "end_datetime", "title", "description", "license", "providers",
                    "created", "updated", "expires"]

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
        """
        Add any additional (not defined in Schema ) keys
        """
        additional_keys = [key for key in in_data.keys() if key not in self.DEFINED_KEYS]
        in_data['additional'] = {key: in_data.pop(key) for key in additional_keys}
        return in_data

    @post_dump
    def add_additional_keys(self, data: dict, **kwargs: dict) -> dict:
        data.update(data.pop('additional'))
        if 'additional' in data.keys():
            data.pop('additional')
        return data


class AssetSchema(BaseSchema):
    href = fields.Url(required=True)
    title = fields.String()
    description = fields.String()
    type = fields.String()
    roles = fields.List(fields.String())
    name = fields.String(required=True)  # Asset's dict key


class LinkSchema(BaseSchema):
    rel = fields.String(required=True)
    href = fields.Url(required=True)
    type = fields.String()
    title = fields.String()


class GeometrySchema(BaseSchema):
    type = fields.String(required=True)  # enum
    coordinates = fields.Raw(required=True)
    # we don't support GeoJson GeometryCollection


class JobResultsBaseSchema(BaseSchema):
    id = fields.String(required=True)
    title = fields.String(required=False)
    description = fields.String(required=False)
    status = fields.String(required=True)
    assets = NestedDict(key="name", nested=AssetSchema)
    stac_version = fields.String(required=True)
    stac_extension = fields.List(fields.String())  # string or url
    links = fields.List(fields.Nested(LinkSchema), required=True)


class JobResultsMetadataSchema(BaseSchema):
    type = fields.String(required=True)
    bbox = fields.List(fields.Float(), required=True)
    geometry = fields.Nested(GeometrySchema, required=True)
    properties = fields.Nested(PropertiesSchema, required=True)
