from marshmallow import Schema, fields, post_load, validates, EXCLUDE
from marshmallow.exceptions import ValidationError
from pycpfcnpj import cpfcnpj


class OwnerSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    _id = fields.String(required=True)
    doc = fields.String(required=True)
    name = fields.String(required=True)
    email = fields.Email(required=True)
    phone = fields.String(missing=None)
    defaulting = fields.String(missing=None)

    @validates('doc')
    def validate_doc(self, value):
        if not cpfcnpj.validate(value):
            raise ValidationError('Invalid CNPJ or CPF')

    @post_load
    def format(self, data: dict, **kwargs):
        fullname = data.pop('name').split(' ', 1)
        data['first_name'] = fullname[0]
        data['last_name'] = fullname[1] if len(fullname) == 2 else None

        return data
