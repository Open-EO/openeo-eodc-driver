from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(required=True)
    user_id = fields.String(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
    active = fields.Boolean(required=True)
    project = fields.String(required=True)
    sa_token = fields.String(required=True)
    admin = fields.Boolean(required=True)
