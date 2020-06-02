from typing import Any, Dict, List, Union
from uuid import uuid4

from marshmallow import Schema, fields, post_dump, post_load, pre_load

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

    def _serialize_basic(self, value: List[Any]) -> Union[List[Any], Any]:
        """
        Converts one value lists to value itself and returns complete list otherwise.
        """
        if len(value) == 1:
            return value[0]
        return value

    def _desrialize_basic(self, value: Any) -> List[Any]:
        """
        Packs non-list values into a list.
        """
        if not isinstance(value, list):
            return [value]
        return value


class SingleMultipleListField(fields.List, SingleMultipleField):
    """
    Handles fields which can be either a schema or a list of schemas.
    """

    def _serialize(self, value: List[Any], attr: str, obj: Any, **kwargs: dict) -> Union[List[Any], Any]:
        """
        Serializes one value list fields to the value itself and returns complete list otherwise.
        """
        value = super()._serialize(value, attr, obj, **kwargs)
        return super()._serialize_basic(value)

    def _deserialize(self, value: Union[List[Any], Any], attr: str, data: Any, **kwargs: dict) -> List[Any]:
        """
        Deserializes non-list fields into a list.
        """
        value = super()._desrialize_basic(value)
        return super()._deserialize(value, attr, data, **kwargs)


class SingleMultiplePluckField(fields.Pluck, SingleMultipleField):
    """
    Handles simple fields which can be either a string or a list of strings.
    """
    def _serialize(self, nested_obj: List[str], attr: str, obj: Any, **kwargs: dict) -> Union[List, Any]:
        """
        Serializes one value list fields to the value itself and returns complete list otherwise.
        """
        value = super()._serialize(nested_obj, attr, obj, **kwargs)
        return super()._serialize_basic(value)

    def _deserialize(self, value: Union[str, List[str]], attr: str, data: Any, **kwargs: dict) -> List[str]:
        """
        Deserializes non-list fields into a list.
        """
        value = super()._desrialize_basic(value)
        return super()._deserialize(value, attr, data, **kwargs)


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


class BaseSchema(Schema):
    __skip_values__: list = [None, []]
    __return_anyway__: list = []
    __model__: Base = None

    @post_dump
    def remove_skip_values(self, data: dict, **kwargs: dict) -> dict:
        """
        Values defined as __skip_values__ should not be dumped, they are removed from the output dict
        """
        return {
            key: value for key, value in data.items()
            if value not in self.__skip_values__ or key in self.__return_anyway__
        }

    @post_load
    def make_object(self, data: dict, **kwargs: dict) -> Base:
        """
        Create a database object from the dict after loading the data.
        """
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
    def cast_default(self, in_data: dict, **kwargs: dict) -> dict:
        """
        Cast the default value to string and add an additional 'default_type' key to store the original type.

        The default value can be of any type, to store it in the database it needs to be casted to string. To later
        return the default value in the original type also the original type is stored as string in the database
        """
        if 'default' in in_data:
            in_data['default_type'] = type(in_data['default']).__name__
            in_data['default'] = str(in_data['default'])
        return in_data

    @post_dump
    def original_default(self, data: dict, **kwargs: dict) -> dict:
        """
        Converts the default value from string to its original type.
        """
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
            _ = data.pop('additional')
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
        if 'returns' in in_data:
            in_data['return_type'] = type(in_data['returns']).__name__
            in_data['returns'] = str(in_data['returns'])
        return in_data

    @post_dump
    def original_returns(self, data: dict, **kwargs: dict) -> dict:
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
    def add_process_graph_id(self, in_data: dict, **kwargs: dict) -> dict:
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
