from marshmallow import Schema, fields

class ProcessSchemaFull(Schema):
    process_id = fields.String(required=True)
    user_id = fields.String(required=True)
    description = fields.String(required=True)
    process_type = fields.String(required=True)
    link = fields.String(required=False)
    args = fields.Dict(required=False)
    git_uri = fields.String(required=False)
    git_ref = fields.String(required=False)
    git_dir = fields.String(required=False)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)

class ProcessSchema(Schema):
    process_id = fields.String(required=True)
    description = fields.String(required=True)
    link = fields.String(required=False)
    args = fields.Dict(required=False)

class ProcessSchemaShort(Schema):
    process_id = fields.String(required=True)
    description = fields.String(required=True)
