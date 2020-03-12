from marshmallow import Schema, fields


class ParameterSchema(Schema):
    name = fields.String(required=True)
    description = fields.String(required=True)
    optional = fields.Boolean(required=False, default=False)
    deprecated = fields.Boolean(required=False, default=False)
    experimental = fields.Boolean(required=False, default=False)
    default = fields.String(required=False)
    schema = fields.List(fields.Nested('SchemaSchema'), attribute='schemas', required=True)  # TODO add switch for single type


class SchemaTypeSchema(Schema):
    name = fields.String(required=True)


class SchemaSchema(Schema):
    type = fields.Nested(SchemaTypeSchema, only='name', many=True, attribute='types', required=False)  # TODO add switch for single type
    subtype = fields.String(required=False)
    parameters = fields.List(fields.Nested(ParameterSchema))
    pattern = fields.String(required=False)
    enum = fields.List(fields.String(), required=False)
    minimum = fields.Float(required=False)
    maximum = fields.Float(required=False)
    minItems = fields.Float(required=False, default=0, attribute='min_items')
    maxItems = fields.Float(required=False, attribute='max_items')


class ReturnSchema(Schema):
    description = fields.String(required=False)
    schema = fields.List(fields.Nested(SchemaSchema), attribute='schemas', required=True)  # TODO add switch for single type


class CategorySchema(Schema):
    name = fields.String(required=True)


class ExceptionSchema(Schema):
    description = fields.String(required=False)
    message = fields.String(required=True)
    http = fields.Integer(required=False, default=400)


class LinkSchema(Schema):
    rel = fields.String(required=True)
    href = fields.String(required=True)
    type = fields.String(required=False)
    title = fields.String(required=False)


class ProcessGraphShortSchema(Schema):
    id = fields.String(required=True, attribute='openeo_id')
    summary = fields.String(required=False)
    description = fields.String(required=False)
    categories = fields.Nested(CategorySchema, only='name', many=True, required=False)
    deprecated = fields.Boolean(required=False, default=False)
    experimental = fields.Boolean(required=False, default=False)
    returns = fields.Nested(ReturnSchema)
    parameters = fields.List(fields.Nested(ParameterSchema))


class ProcessGraphFullSchema(ProcessGraphShortSchema):
    exceptions = fields.List(fields.Nested(ExceptionSchema), required=False)  # TODO upgrade to marshmallow version 3 to be fully compliant
    examples = fields.Dict(required=False)
    links = fields.List(fields.Nested(LinkSchema), required=False)
    process_graph = fields.Dict(required=True)
