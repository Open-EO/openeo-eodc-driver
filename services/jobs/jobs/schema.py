from typing import Any, Optional
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


class JobShortSchema(BaseSchema, MoneyConverter):
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


class PropertiesSchema(BaseSchema):
    datetime = fields.DateTime(required=True)
    start_datetime = fields.DateTime()
    end_datetime = fields.DateTime()
    title = fields.String()
    description = fields.String()
    license = fields.String()  # Stac license
    providers = fields.List(fields.String())
    created = fields.DateTime()
    updated = fields.DateTime()
    expires = fields.DateTime()
    # TODO add support for anything!


class AssetSchema(BaseSchema):
    href = fields.Url(required=True)
    title = fields.String()
    description = fields.String()
    type = fields.String()
    roles = fields.List(fields.String())


class LinkSchema(BaseSchema):
    rel = fields.String(required=True)
    href = fields.Url(required=True)
    type = fields.String()
    title = fields.String()


class JobResultsSchema(BaseSchema):
    stac_version = fields.String(required=True)
    stac_extension = fields.List(fields.String())  # string or url
    id = fields.String(required=True)
    type = fields.String(required=True)  # TODO what is this?
    bbox = fields.List(fields.Float(), required=True)
    title = fields.String(required=False)
    description = fields.String(required=False)
    status = fields.String(required=True)
    updated = fields.DateTime(attribute="updated_at", required=False)
    properties = fields.Nested(PropertiesSchema, required=True)
    # assets = fields.List(AssetSchema, required=True)  # TODO should be dict
    # links = fields.List(LinkSchema, required=True)
