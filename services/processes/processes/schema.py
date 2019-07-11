from marshmallow import Schema, fields


class ProcessGraphSchema(Schema):
    process_id = fields.String(required=True)
    process_description = fields.String()


class ProcessNodeSchema(Schema):
    id = fields.String(required=True)
    seq_num = fields.Integer(required=True)
    process_id = fields.String(required=True)
    imagery_id = fields.String(required=True)
    args = fields.Dict(required=True)


class ProcessGraphShortSchema(Schema):
    process_graph_id = fields.String(attribute="id", required=True)
    title = fields.String(required=False)
    description = fields.String(required=False)


class ProcessGraphFullSchema(Schema):
    process_graph_id = fields.String(attribute="id", required=True)
    title = fields.String(required=False)
    description = fields.String(required=False)
    process_graph = fields.Dict(required=True)
