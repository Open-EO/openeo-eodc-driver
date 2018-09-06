from marshmallow import Schema, fields, validate
import pprint


class DictField(fields.Field):
    def __init__(self, key_field, nested_field, *args, **kwargs):
        fields.Field.__init__(self, *args, **kwargs)
        self.key_field = key_field
        self.nested_field = nested_field

    def _deserialize(self, value, attr, obj):
        if not value: return None

        ret = {}
        for key, val in value.items():
            k = self.key_field.deserialize(key)
            v = self.nested_field.deserialize(val)
            ret[k] = v
        return ret

    def _serialize(self, value, attr, obj):
        if not value: return None

        ret = {}
        for key, val in value.items():
            k = self.key_field._serialize(key, attr, obj)
            v = self.nested_field.serialize(key, self.get_value(attr, obj))
            ret[k] = v

        return ret


class ParameterField(fields.Field):
    def __init__(self, array_field, *args, **kwargs):
        fields.Field.__init__(self, *args, **kwargs)
        self.array_field = array_field

    def _serialize(self, parameter_array, attr, obj):
        if not parameter_array: return None

        ret = {}
        for parameter in parameter_array:
            ret[parameter.name] = self.array_field._serialize(parameter, attr, obj)

        return ret


class LinksSchema(Schema):
    href = fields.Url(required=True)
    rel = fields.String()
    type = fields.String()
    title = fields.String()


class ReturnSchema(Schema):
    description = fields.String(required=True)
    schema = fields.Dict(required=True)
    mime_type = fields.String()


class ExceptionSchema(Schema):
    code = fields.Integer(required=True)
    description = fields.String(required=True)


class ProcessGraphSchema(Schema):
    process_id = fields.String(required=True)
    process_description = fields.String()


class ExampleSchema(Schema):
    description = fields.String(required=True)
    summary = fields.String()
    process_graph = fields.Nested(ProcessGraphSchema)


class DependencySchema(Schema):
    parameter = fields.String(
        required=True, validate=validate.Regexp(r'^[a-zA-Z\_\-\d]+$'))
    description = fields.String()
    ref_values = fields.List(fields.Raw())


class ParameterSchema(Schema):
    description = fields.String(required=True)
    required = fields.Boolean(default=False)
    dependencies = fields.Nested(DependencySchema, many=True)
    deprecated = fields.Boolean(default=False)
    mime_type = fields.String()
    schema = fields.Dict(required=True)


class ProcessSchema(Schema):
    name = fields.String(
        required=True, validate=validate.Regexp(r'^[a-zA-Z\_\-\d]+$'))
    description = fields.String(required=True)
    summary = fields.String()
    min_parameters = fields.Integer()
    deprecated = fields.Boolean(default=False)
    parameters = ParameterField(fields.Nested(ParameterSchema))
    examples = DictField(
        fields.String(validate=validate.Regexp(r'^[a-zA-Z\_\-\d]+$')),
        fields.Nested(ExampleSchema), many=True)
    exceptions = DictField(
        fields.String(validate=validate.Regexp(r'^[a-zA-Z\_\-\d]+$')),
        fields.Nested(ExceptionSchema))
    returns = fields.Nested(ReturnSchema)
    links = fields.Nested(LinksSchema, many=True)
    p_type = fields.String(required=True)


class ProcessNodeSchema(Schema):
    id = fields.String(required=True)
    seq_num = fields.Integer(required=True)
    process_id = fields.String(required=True)
    imagery_id = fields.String(required=True)
    args =  fields.Dict(required=True)


class ProcessGraphShortSchema(Schema):
    process_graph_id = fields.String(attribute="id", required=True)
    title = fields.String(required=False)
    description = fields.String(required=False)


class ProcessGraphFullSchema(Schema):
    process_graph_id = fields.String(attribute="id", required=True)
    title = fields.String(required=False)
    description = fields.String(required=False)
    process_graph = fields.Dict(required=True)
