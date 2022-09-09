from marshmallow import Schema, fields


class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class TokenSchema(Schema):
    token = fields.String(required=True)
