"""Provides all schemas definitions used in the main service to serialize and deserialize data.

Schemas are defined to fit request return schemas defined in the `OpenEO API EO Data Discovery`_ and the database
models defined in :py:mod:`~processes.models`.
"""
import re
from typing import Any, Dict, List, Union
from uuid import uuid4

from marshmallow import Schema, fields, post_dump, post_load, pre_load, validate

from .models import Base, Category, Example, ExceptionCode, Link, Parameter, ProcessGraph, Return, Schema as DbSchema, \
    SchemaEnum, SchemaType

type_map = {
    "int": lambda x: int(x),
    "float": lambda x: float(x),
    "bool": lambda x: bool(x),
    "str": lambda x: str(x),
    "NoneType": lambda x: None
}


class SingleMultipleField:
    """Allow to swap between one-value list and value itself."""

    def _serialize_basic(self, value: List[Any]) -> Union[List[Any], Any]:
        """Convert one value lists to value itself and returns complete list otherwise."""
        if len(value) == 1:
            return value[0]
        return value

    def _desrialize_basic(self, value: Any) -> List[Any]:
        """Pack non-list values into a list."""
        if not isinstance(value, list):
            return [value]
        return value


class SingleMultipleListField(fields.List, SingleMultipleField):
    """Handle fields which can be either a schema or a list of schemas."""

    def _serialize(self, value: List[Any], attr: str, obj: Any, **kwargs: dict) -> Union[List[Any], Any]:
        """Serialize one value list fields to the value itself and returns complete list otherwise."""
        value = super()._serialize(value, attr, obj, **kwargs)
        return super()._serialize_basic(value)

    def _deserialize(self, value: Union[List[Any], Any], attr: str, data: Any, **kwargs: dict) -> List[Any]:
        """Deserialize non-list fields into a list."""
        value = super()._desrialize_basic(value)
        return super()._deserialize(value, attr, data, **kwargs)


class SingleMultiplePluckField(fields.Pluck, SingleMultipleField):
    """Handle simple fields which can be either a string or a list of strings."""

    def _serialize(self, nested_obj: List[str], attr: str, obj: Any, **kwargs: dict) -> Union[List, Any]:
        """Serialize one value list fields to the value itself and returns complete list otherwise."""
        value = super()._serialize(nested_obj, attr, obj, **kwargs)
        return super()._serialize_basic(value)

    def _deserialize(self, value: Union[str, List[str]], attr: str, data: Any, **kwargs: dict) -> List[str]:
        """Deserialize non-list fields into a list."""
        value = super()._desrialize_basic(value)
        return super()._deserialize(value, attr, data, **kwargs)


class NestedDict(fields.Nested):
    """Allow nesting a schema inside a dictionary.

    This is analogous to nesting a schema inside a list but using a dictionary with a given key instead.
    """

    def __init__(self, nested: Any, key: str, *args: set, **kwargs: dict) -> None:
        """Initialize nested dictionary field."""
        super().__init__(nested, many=True, *args, **kwargs)
        self.key = key

    def _serialize(self, nested_obj: List[Any], attr: str, obj: Any, **kwargs: dict) \
            -> Dict[str, Any]:
        """Convert a list of nested objects into a dictionary of dictionaries using the key.

        input: key: 'foo', nested_obj: [SomeSchema(foo=1, bar=2, baz=3), SomeSchema(foo=4, bar=1, baz=0)]
        output: {1: {bar: 2, baz: 3}, 4: {bar: 1, baz: 0}}
        """
        nested_list = super()._serialize(nested_obj, attr, obj)
        nested_dict = {item.pop(self.key): item for item in nested_list}
        return nested_dict

    def _deserialize(self, value: Dict[str, Any], attr: str, data: Any, **kwargs: dict) \
            -> List[Any]:
        """Convert a dictionary of dictionaries into a list of nested objects.

        input: key: foo, value: {1: {bar: 2, baz: 3}, 4: {bar: 1, baz: 0}}
        output: [SomeSchema(foo=1, bar=2, baz=3), SomeSchema(foo=4, bar=1, baz=0)]
        """
        raw_list = []
        for key, item in value.items():
            item[self.key] = key
            raw_list.append(item)
        nested_list = super()._deserialize(raw_list, attr, data)
        return nested_list


class BaseSchema(Schema):
    """Base Schema including functionality useful in all other schemas."""

    __skip_values__: list = [None, []]
    """Key value pairs where the value is one of these will not be dumped.

    There is no need to return unset keys and overload returned dictionaries with 'meaningless' key value pairs.
    """
    __return_anyway__: list = []
    """These keys will always be returned, also if their value is in __skip_values__.

    Therefore __return_anyway__ overwrites __skip_values__. This is useful if a return key is required by the
    `OpenEO API`_ but it's value may be in __skip_values__.
    """
    __model__: Base = None
    """Database table model corresponding to the schema."""

    @post_dump
    def remove_skip_values(self, data: dict, **kwargs: dict) -> dict:
        """Remove keys where value is in __skip_values__ but key is not in __return_anyway__."""
        return {
            key: value for key, value in data.items()
            if value not in self.__skip_values__ or key in self.__return_anyway__
        }

    @post_load
    def make_object(self, data: dict, **kwargs: dict) -> Base:
        """Create a database object from the dict after loading the data."""
        if self.__model__:
            return self.__model__(**data)


class ParameterSchema(BaseSchema):
    """Schema for parameters."""

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
    def cast_default(self, in_data: dict, **kwargs: dict) -> dict:
        """Cast the default value to string and add an additional 'default_type' key to store the original type.

        The default value can be of any type, but to store it in the database it needs to be casted to string. To later
        return the default value in the original type also the original type is stored as string in a separate database
        column.
        """
        if 'default' in in_data:
            in_data['default_type'] = type(in_data['default']).__name__
            in_data['default'] = str(in_data['default'])
        return in_data

    @post_dump
    def original_default(self, data: dict, **kwargs: dict) -> dict:
        """Convert the default value from string to its original type."""
        if data['default'] and data['default_type'] in type_map.keys():
            data['default'] = type_map[data.pop('default_type')](data['default'])
        else:
            data.pop('default_type')
        return data


class SchemaTypeSchema(BaseSchema):
    """Schema for schema type."""

    __model__ = SchemaType

    name = fields.String(required=True)


class SchemaEnumSchema(BaseSchema):
    """Schema for schema enum."""

    __model__ = SchemaEnum

    name = fields.String(required=True)


class SchemaSchema(BaseSchema):
    """Schema for schema."""

    __model__ = DbSchema
    DEFINED_KEYS = ['type', 'subtype', 'parameters', 'pattern', 'enum', 'minimum', 'maximum', 'minItems', 'maxItems',
                    'items']
    """List of all defined keys in this schema."""

    type_ = SingleMultiplePluckField(SchemaTypeSchema, 'name', many=True, data_key="type", attribute='types')
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
    def separate_additional_keys(self, in_data: dict, **kwargs: dict) -> dict:
        """Add any additional keys - not defined in Schema / :py:attr:`~processes.models.SchemaSchema.DEFINED_KEY."""
        additional_keys = [key for key in in_data.keys() if key not in self.DEFINED_KEYS]
        in_data['additional'] = {key: in_data.pop(key) for key in additional_keys}
        return in_data

    @post_dump
    def add_additional_keys(self, data: dict, **kwargs: dict) -> dict:
        """Add keys stored in the addition keys."""
        data.update(data.pop('additional'))
        if 'additional' in data.keys():
            _ = data.pop('additional')
        return data


class ReturnSchema(BaseSchema):
    """Schema for return entity."""

    __model__ = Return

    description = fields.String(required=False)
    schema = SingleMultipleListField(fields.Nested(SchemaSchema), attribute='schemas', required=True)


class CategorySchema(BaseSchema):
    """Schema for category."""

    __model__ = Category

    name = fields.String(required=True)


class ExceptionSchema(BaseSchema):
    """Schema for exception."""

    __model__ = ExceptionCode

    description = fields.String(required=False)
    message = fields.String(required=True)
    http = fields.Integer(required=False, default=400)
    error_code = fields.String(required=True)  # Exception's dict key


class LinkSchema(BaseSchema):
    """Schema for link."""

    __model__ = Link

    rel = fields.String(required=True)
    href = fields.Url(required=True)
    type_ = fields.String(attribute="type", data_key="type")
    title = fields.String()


class ExampleSchema(BaseSchema):
    """Schema for example."""

    __return_anyway__ = ['returns']
    __model__ = Example

    process_graph = fields.Dict()
    arguments = fields.Dict()
    title = fields.String(allow_none=True)
    description = fields.String(allow_none=True)
    returns = fields.String(allow_none=True)
    return_type = fields.String(allow_none=True)

    @pre_load
    def cast_returns(self, in_data: dict, **kwargs: dict) -> dict:
        """Cast return value to string and store original type separately."""
        if 'returns' in in_data:
            in_data['return_type'] = type(in_data['returns']).__name__
            in_data['returns'] = str(in_data['returns'])
        return in_data

    @post_dump
    def original_returns(self, data: dict, **kwargs: dict) -> dict:
        """Cast return value back to original type."""
        if data['returns'] and data['return_type'] in type_map.keys():
            data['returns'] = type_map[data.pop('return_type')](data['returns'])
        else:
            data.pop('return_type')
        return data


class ProcessGraphShortSchema(BaseSchema):
    """Schema including basic information about a process graph."""

    id_internal = fields.String(attribute='id', load_only=True)
    id_ = fields.String(required=True, data_key="id", attribute='id_openeo', validate=validate.Regexp(regex='^\\w+$'))
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
    def add_process_graph_id(self, in_data: dict, **kwargs: dict) -> dict:
        """Generate and store an internal process_graph_id."""
        if not ('id_internal' in in_data and in_data['id_internal']):
            in_data['id_internal'] = 'pg-' + str(uuid4())
        return in_data

    @post_dump
    def fix_old_process_graph_ids(self, data: dict, **kwargs: dict) -> dict:
        """Reformat id_openeo to match required regex.

        Due to backward compatibility some process_graph ids may contain '-' which are not allowed.
        '-' are replaced by '_' and the ids are prefixed with 'regex_'
        """
        id_pattern = re.compile('^\\w+$')
        if id_pattern.match(data['id']) is None:
            regex_id = data['id'].replace('-', '_')
            data['id'] = 'regex_' + regex_id
        return data


class ProcessGraphFullSchema(ProcessGraphShortSchema):
    """Schema including detailed information about a process graph."""

    __model__ = ProcessGraph

    exceptions = NestedDict(key='error_code', nested=ExceptionSchema)
    examples = fields.List(fields.Nested(ExampleSchema))
    links = fields.List(fields.Nested(LinkSchema))
    process_graph = fields.Dict(required=True)


class ProcessGraphPredefinedSchema(ProcessGraphShortSchema):
    """Schema including detailed information of a process graph, but no process graph definition.

    This is used for predefined processes as they do not need to have a process grah attached.
    """

    __return_anyway__ = ['parameters']
    __model__ = ProcessGraph

    exceptions = NestedDict(key='error_code', nested=ExceptionSchema)
    examples = fields.List(fields.Nested(ExampleSchema))
    links = fields.List(fields.Nested(LinkSchema))
    process_graph = fields.Dict()
