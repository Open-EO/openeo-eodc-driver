import typing
from uuid import uuid4

from marshmallow import Schema, fields, post_dump, post_load, pre_load

from processes.models import Link, ExceptionCode, Category, Return, Schema as DbSchema, SchemaEnum, SchemaType, \
    Parameter, ProcessGraph, Example

type_map = {
    "int": lambda x: int(x),
    "float": lambda x: float(x),
    "bool": lambda x: bool(x),
    "str": lambda x: str(x)
}


class SingleMultipleField:

    def _serialize_basic(self, value):
        if len(value) == 1:
            return value[0]
        return value

    def _desrialize_basic(self, value):
        if not isinstance(value, list):
            return [value]
        return value


class SingleMultipleListField(fields.List, SingleMultipleField):
    def _serialize(self, value, attr, obj, **kwargs):
        value = super()._serialize(value, attr, obj, **kwargs)
        return super()._serialize_basic(value)

    def _deserialize(self, value, attr, data, **kwargs) -> typing.List[typing.Any]:
        value = super()._desrialize_basic(value)
        return super()._deserialize(value, attr, data, **kwargs)


class SingleMultiplePluckField(fields.Pluck, SingleMultipleField):
    def _serialize(self, nested_obj, attr, obj, **kwargs):
        value = super()._serialize(nested_obj, attr, obj, **kwargs)
        return super()._serialize_basic(value)

    def _deserialize(self, value, attr, data, **kwargs):
        value = super()._desrialize_basic(value)
        return super()._deserialize(value, attr, data, **kwargs)


class NestedDict(fields.Nested):
    def __init__(self, nested, key, *args, **kwargs):
        super().__init__(nested, many=True, *args, **kwargs)
        self.key = key

    def _serialize(self, nested_obj, attr, obj, **kwargs):
        nested_list = super()._serialize(nested_obj, attr, obj)
        nested_dict = {item.pop(self.key): item for item in nested_list}
        return nested_dict

    def _deserialize(self, value, attr, data, **kwargs):
        raw_list = []
        for key, item in value.items():
            item[self.key] = key
            raw_list.append(item)
        nested_list = super()._deserialize(raw_list, attr, data)
        return nested_list


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


class ParameterSchema(BaseSchema):
    __model__ = Parameter

    name = fields.String(required=True)
    description = fields.String(required=True)
    optional = fields.Boolean(default=False)
    deprecated = fields.Boolean(default=False)
    experimental = fields.Boolean(default=False)
    default = fields.String(allow_none=True)
    default_type = fields.String(allow_none=True)
    schema = SingleMultipleListField(fields.Nested(lambda: SchemaSchema()), attribute='schemas', required=True)

    @pre_load
    def cast_default(self, in_data, **kwargs):
        if 'default' in in_data:
            in_data['default_type'] = type(in_data['default']).__name__
            in_data['default'] = str(in_data['default'])
        return in_data

    @post_dump
    def original_default(self, data, **kwargs):
        if data['default'] and data['default_type'] in type_map.keys():
            data['default'] = type_map[data.pop('default_type')](data['default'])
        else:
            data.pop('default_type')
        return data


class SchemaTypeSchema(BaseSchema):
    __model__ = SchemaType

    name = fields.String(required=True)


class SchemaEnumSchema(BaseSchema):
    __model__ = SchemaEnum

    name = fields.String(required=True)


class SchemaSchema(BaseSchema):
    __model__ = DbSchema
    DEFINED_KEYS = ['type', 'subtype', 'parameters', 'pattern', 'enum', 'minimum', 'maximum', 'minItems', 'maxItems',
                    'items']

    type = SingleMultiplePluckField(SchemaTypeSchema, 'name', many=True, attribute='types')
    subtype = fields.String()
    parameters = fields.List(fields.Nested(ParameterSchema))
    pattern = fields.String()
    enum = fields.Pluck(SchemaEnumSchema, 'name', many=True, attribute='enums')
    minimum = fields.Float()
    maximum = fields.Float()
    minItems = fields.Float(default=0, attribute='min_items')
    maxItems = fields.Float(attribute='max_items')
    items = fields.Dict()
    additional = fields.Dict()

    @pre_load
    def separate_additional_keys(self, in_data, **kwargs):
        additional_keys = [key for key in in_data.keys() if key not in self.DEFINED_KEYS]
        in_data['additional'] = {key: in_data.pop(key) for key in additional_keys}
        return in_data

    @post_dump
    def add_additional_keys(self, data, **kwargs):
        if len(data['additional'].keys()) > 0:
            data.update(data.pop('additional'))
        data.pop('additional')
        return data


class ReturnSchema(BaseSchema):
    __model__ = Return

    description = fields.String(required=False)
    schema = SingleMultipleListField(fields.Nested(SchemaSchema), attribute='schemas', required=True)


class CategorySchema(BaseSchema):
    __model__ = Category

    name = fields.String(required=True)


class ExceptionSchema(BaseSchema):
    __model__ = ExceptionCode

    description = fields.String(required=False)
    message = fields.String(required=True)
    http = fields.Integer(required=False, default=400)
    error_code = fields.String(required=True)


class LinkSchema(BaseSchema):
    __model__ = Link

    rel = fields.String(required=True)
    href = fields.Url(required=True)
    type = fields.String()
    title = fields.String()


class ExampleSchema(BaseSchema):
    __model__ = Example

    process_graph = fields.Dict()
    arguments = fields.Dict()
    title = fields.String(allow_none=True)
    description = fields.String(allow_none=True)
    returns = fields.String(allow_none=True)
    return_type = fields.String(allow_none=True)

    @pre_load
    def cast_returns(self, in_data, **kwargs):
        if 'returns' in in_data:
            in_data['return_type'] = type(in_data['returns']).__name__
            in_data['returns'] = str(in_data['returns'])
        return in_data

    @post_dump
    def original_returns(self, data, **kwargs):
        if data['returns'] and data['return_type'] in type_map.keys():
            data['returns'] = type_map[data.pop('return_type')](data['returns'])
        else:
            data.pop('return_type')
        return data


class ProcessGraphShortSchema(BaseSchema):
    id_internal = fields.String(attribute='id', load_only=True)
    id = fields.String(required=True, attribute='id_openeo')
    summary = fields.String()
    description = fields.String()
    categories = fields.Pluck(CategorySchema, 'name', many=True)
    deprecated = fields.Boolean(default=False)
    experimental = fields.Boolean(default=False)
    returns = fields.Nested(ReturnSchema)
    parameters = fields.List(fields.Nested(ParameterSchema))
    process_definition = fields.Field(load_only=True)
    user_id = fields.String(load_only=True)

    @pre_load
    def add_process_graph_id(self, in_data, **kwargs):
        if not ('id_internal' in in_data and in_data['id_internal']):
            in_data['id_internal'] = 'pg-' + str(uuid4())
        return in_data


class ProcessGraphFullSchema(ProcessGraphShortSchema):
    __model__ = ProcessGraph

    exceptions = NestedDict(key='error_code', nested=ExceptionSchema)
    examples = fields.List(fields.Nested(ExampleSchema))
    links = fields.List(fields.Nested(LinkSchema))
    process_graph = fields.Dict(required=True)


class ProcessGraphPredefinedSchema(ProcessGraphShortSchema):
    __model__ = ProcessGraph

    exceptions = NestedDict(key='error_code', nested=ExceptionSchema)
    examples = fields.List(fields.Nested(ExampleSchema))
    links = fields.List(fields.Nested(LinkSchema))
    process_graph = fields.Dict()
