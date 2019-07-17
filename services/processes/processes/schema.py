from marshmallow import Schema, fields


class ProcessGraphSchema(Schema):
    process_id = fields.String(required=True)
    process_description = fields.String()


class ProcessGraphShortSchema(Schema):
    id = fields.String(required=True)
    title = fields.String(required=False)
    description = fields.String(required=False)


class ProcessGraphFullSchema(Schema):
    id = fields.String(required=True)
    title = fields.String(required=False)
    description = fields.String(required=False)
    process_graph = fields.Dict(required=True)
