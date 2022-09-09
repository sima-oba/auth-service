from marshmallow import Schema, fields, EXCLUDE


class GroupSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    name = fields.String(required=True)
    roles = fields.List(fields.String(), missing=[])
