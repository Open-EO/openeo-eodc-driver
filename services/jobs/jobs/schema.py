from marshmallow import Schema, fields

class JobSchema(Schema):
    job_id = fields.Str(attribute="id", required=True)
    title = fields.Str(required=False)
    description = fields.Str(required=False)
    status = fields.Str(required=False)
    submitted = fields.DateTime(attribute="created_at", required=True)
    updated = fields.DateTime(attribute="updated_at", required=True)
    plan = fields.Str(required=False)
    costs = fields.Int(attribute="current_costs", required=False)
    budget = fields.Int(required=False)


class JobSchemaFull(Schema):
    job_id = fields.Str(attribute="id", required=True)
    title = fields.Str(required=False)
    description = fields.Str(required=False)
    process_graph = fields.Dict(required=True)
    output = fields.Dict(required=False)
    status = fields.Str(required=False)
    submitted = fields.DateTime(attribute="created_at", required=True)
    updated = fields.DateTime(attribute="updated_at", required=True)
    plan = fields.Str(required=False)
    costs = fields.Int(attribute="current_costs", required=False)
    budget = fields.Int(required=False)
    logs = fields.Str(required=False)
    metrics = fields.Dict(many=True, required=False)
