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

    def to_euro(self, obj):
        if obj:
            return obj.budget / 100.0


class JobSchema(BaseSchema):
    id = fields.String(required=True)
    title = fields.String()
    description = fields.String()
    status = fields.String(required=True)
    created = fields.DateTime(attribute="created_at", required=True)
    updated = fields.DateTime(attribute="updated_at")
    plan = fields.String()
    costs = fields.Integer(attribute="current_costs")
    budget = fields.Integer()


class JobSchemaFull(Schema, MoneyConverter):
    id = fields.String(required=True)
    title = fields.String()
    description = fields.String()
    process = fields.Dict(required=True)
    status = fields.String(required=True)
    progress = fields.Float()  # in database?
    created = fields.DateTime(attribute="created_at", required=True)
    updated = fields.DateTime(attribute="updated_at")
    plan = fields.String()
    costs = fields.Method('to_euro', deserialize='to_cent', attribute="current_costs")
    budget = fields.Method('to_euro', deserialize='to_cent')


class JobSchemaShort(Schema):
    id = fields.Str(required=True)
    title = fields.Str(required=False)
    description = fields.Str(required=False)
    status = fields.Str(required=True)
    updated = fields.DateTime(attribute="updated_at", required=False)


class JobCreateSchema(BaseSchema, MoneyConverter):
    __model__ = Job

    id = fields.String(required=True)
    user_id = fields.String(required=True)
    title = fields.String()
    description = fields.String()
    process_graph_id = fields.String(required=True)
    plan = fields.String()
    budget = fields.Method('to_euro', deserialize='to_cent')

    @pre_load
    def add_process_graph_id(self, in_data, **kwargs):
        in_data['id'] = 'jb-' + str(uuid4())
        return in_data
