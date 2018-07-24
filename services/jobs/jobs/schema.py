from marshmallow import Schema, fields

class JobSchema(Schema):
    job_id = fields.Str(attribute="id", required=True)
    status = fields.Str(required=True)
    submitted = fields.DateTime(attribute="created_at", required=True)
    updated = fields.DateTime(attribute="updated_at", required=True)
    user_id = fields.Str(required=True)
    consumed_credits = fields.Int(attribute="credits", required=True)


class JobSchemaFull(Schema):
    job_id = fields.Str(attribute="id", required=True)
    status = fields.Str(required=True)
    submitted = fields.DateTime(attribute="created_at", required=True)
    updated = fields.DateTime(attribute="updated_at", required=True)
    user_id = fields.Str(required=True)
    consumed_credits = fields.Int(attribute="credits", required=True)
    process_graph = fields.Dict(required=True)
    output = fields.Dict(required=True)
