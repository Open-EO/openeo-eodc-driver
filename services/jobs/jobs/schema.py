from marshmallow import Schema, fields


class JobSchema(Schema):
    id = fields.Str(required=True)
    title = fields.Str(required=False)
    description = fields.Str(required=False)
    status = fields.Str(required=True)
    submitted = fields.DateTime(attribute="created_at", required=True)
    updated = fields.DateTime(attribute="updated_at", required=False)
    plan = fields.Str(required=False)
    costs = fields.Int(attribute="current_costs", required=False)
    budget = fields.Int(required=False)


class JobSchemaFull(Schema):
    id = fields.Str(required=True)
    title = fields.Str(required=False)
    description = fields.Str(required=False)
    process_graph = fields.Dict(required=True)
    status = fields.Str(required=True)
    progress = fields.Str(required=False)
    error = fields.Dict(required=False)
    submitted = fields.DateTime(attribute="created_at", required=True)
    updated = fields.DateTime(attribute="updated_at", required=False)
    plan = fields.Str(required=False)
    costs = fields.Int(attribute="current_costs", required=False)
    budget = fields.Int(required=False)
