from marshmallow import Schema, fields, validate
import pprint


class DictField(fields.Field):
    def __init__(self, key_field, nested_field, *args, **kwargs):
        fields.Field.__init__(self, *args, **kwargs)
        self.key_field = key_field
        self.nested_field = nested_field

    def _deserialize(self, value, attr, obj):
        ret = {}
        for key, val in value.items():
            k = self.key_field.deserialize(key)
            v = self.nested_field.deserialize(val)
            ret[k] = v
        return ret

    def _serialize(self, value, attr, obj):
        ret = {}
        for key, val in value.items():
            k = self.key_field._serialize(key, attr, obj)
            v = self.nested_field.serialize(key, self.get_value(attr, obj))
            ret[k] = v
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
    parameters = DictField(
        fields.String(validate=validate.Regexp(r'^[a-zA-Z\_\-\d]+$')),
        fields.Nested(ParameterSchema))
    exceptions = DictField(
        fields.String(validate=validate.Regexp(r'^[a-zA-Z\_\-\d]+$')),
        fields.Nested(ExceptionSchema))
    examples = DictField(
        fields.String(validate=validate.Regexp(r'^[a-zA-Z\_\-\d]+$')),
        fields.Nested(ExampleSchema))
    returns = fields.Nested(ReturnSchema)
    links = fields.Nested(LinksSchema, many=True)


# class ProcessSchemaFull(Schema):
#     process_id = fields.String(required=True)
#     user_id = fields.String(required=True)
#     description = fields.String(required=True)
#     process_type = fields.String(required=True)
#     link = fields.String(required=False)
#     args = fields.Dict(required=False)
#     git_uri = fields.String(required=False)
#     git_ref = fields.String(required=False)
#     git_dir = fields.String(required=False)
#     created_at = fields.DateTime(required=True)
#     updated_at = fields.DateTime(required=True)

# class ProcessSchema(Schema):
#     process_id = fields.String(required=True)
#     description = fields.String(required=True)
#     link = fields.String(required=False)
#     args = fields.Dict(required=False)

# class ProcessSchemaShort(Schema):
#     process_id = fields.String(required=True)
#     description = fields.String(required=True)
