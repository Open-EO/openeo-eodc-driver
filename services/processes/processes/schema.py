from marshmallow import Schema, fields, post_dump


class SingleMultipleListField(fields.List):
    def _serialize(self, value, attr, obj, **kwargs):
        value = super()._serialize(value, attr, obj, **kwargs)
        if len(value) == 1:
            return value[0]
        return value


class SingleMultiplePluckField(fields.Pluck):
    def _serialize(self, nested_obj, attr, obj, **kwargs):
        value = super()._serialize(nested_obj, attr, obj, **kwargs)
        if len(value) == 1:
            return value[0]
        return value


class NestedDict(fields.Nested):
    def __init__(self, nested, key, *args, **kwargs):
        super().__init__(nested, many=True, *args, **kwargs)
        self.key = key

    def _serialize(self, nested_obj, attr, obj, **kwargs):
        nested_list = super()._serialize(nested_obj, attr, obj)
        nested_dict = {item.pop(self.key): item for item in nested_list}
        return nested_dict


class BaseSchema(Schema):
    SKIP_VALUES = [None, []]

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value not in self.SKIP_VALUES
        }


class ParameterSchema(BaseSchema):
    name = fields.String(required=True)
    description = fields.String(required=True)
    optional = fields.Boolean(required=False, default=False)
    deprecated = fields.Boolean(required=False, default=False)
    experimental = fields.Boolean(required=False, default=False)
    default = fields.String(required=False)
    schema = SingleMultipleListField(fields.Nested(lambda: SchemaSchema()), attribute='schemas', required=True)


class SchemaTypeSchema(BaseSchema):
    name = fields.String(required=True)


class SchemaEnumSchema(BaseSchema):
    name = fields.String(required=True)


class SchemaSchema(BaseSchema):
    type = SingleMultiplePluckField(SchemaTypeSchema, 'name', many=True, attribute='types', required=False)
    subtype = fields.String(required=False)
    parameters = fields.List(fields.Nested(ParameterSchema))
    pattern = fields.String(required=False)
    enum = fields.Pluck(SchemaEnumSchema, 'name', many=True, attribute='enums', required=False)
    minimum = fields.Float(required=False)
    maximum = fields.Float(required=False)
    minItems = fields.Float(required=False, default=0, attribute='min_items')
    maxItems = fields.Float(required=False, attribute='max_items')
    items = fields.List(fields.Nested(SchemaEnumSchema), attribute='schemas', required=False)


class ReturnSchema(BaseSchema):
    description = fields.String(required=False)
    schema = SingleMultipleListField(fields.Nested(SchemaSchema), attribute='schemas', required=True)


class CategorySchema(BaseSchema):
    name = fields.String(required=True)


class ExceptionSchema(BaseSchema):
    description = fields.String(required=False)
    message = fields.String(required=True)
    http = fields.Integer(required=False, default=400)
    error_code = fields.String(required=True)


class LinkSchema(BaseSchema):
    rel = fields.String(required=True)
    href = fields.String(required=True)
    type = fields.String(required=False)
    title = fields.String(required=False)


class ProcessGraphShortSchema(BaseSchema):
    id = fields.String(required=True, attribute='openeo_id')
    summary = fields.String(required=False)
    description = fields.String(required=False)
    categories = fields.Pluck(CategorySchema, 'name', many=True, required=False)
    deprecated = fields.Boolean(required=False, default=False)
    experimental = fields.Boolean(required=False, default=False)
    returns = fields.Nested(ReturnSchema)
    parameters = fields.List(fields.Nested(ParameterSchema))


class ProcessGraphFullSchema(ProcessGraphShortSchema):
    exceptions = NestedDict(key='error_code', nested=ExceptionSchema, required=False)
    examples = fields.Dict(required=False)
    links = fields.List(fields.Nested(LinkSchema), required=False)
    process_graph = fields.Dict(required=True)
