from marshmallow import Schema, ValidationError, fields, validates, EXCLUDE
from pycpfcnpj import cpfcnpj


class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    doc = fields.String(required=True)
    enabled = fields.Boolean(misssing=False)
    firstName = fields.String(required=True)
    lastName = fields.String(required=True)
    roles = fields.List(fields.String(), missing=[])
    groups = fields.List(fields.String(), missing=[])


class NewUserSchema(Schema):
    doc = fields.String(required=True)
    email = fields.Email(required=True)
    name = fields.String(required=True)
    phone = fields.String(required=True)

    @validates('doc')
    def validate_doc(self, value):
        if not cpfcnpj.validate(value):
            raise ValidationError('Invalid CNPJ or CPF')


class PasswordSchema(Schema):
    password = fields.String(required=True)


class UsernameSchema(Schema):
    username = fields.Email(required=True)
