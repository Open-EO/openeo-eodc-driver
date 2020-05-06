from uuid import uuid4

from marshmallow import Schema, fields, post_load, pre_load, post_dump

from .models import Job


class BaseSchema(Schema):
    __skip_values__ = [None, []]
    __model__ = None

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value not in self.__skip_values__
        }

    @post_load
    def make_object(self, data, **kwargs):
        if self.__model__:
            return self.__model__(**data)


class MoneyConverter:
    def to_cent(self, obj):
        if obj:
            return int(obj * 100)

    def to_euro_budget(self, obj):
        if obj.budget:
            return obj.budget / 100.0

    def to_euro_cost(self, obj):
        if obj.current_costs:
            return obj.current_costs / 100.0


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
    def add_process_graph_id(self, in_data, **kwargs):
        in_data['id'] = 'jb-' + str(uuid4())
        return in_data
class JobResultsSchema(BaseSchema):
    id = fields.String(required=True)
