from base64 import urlsafe_b64decode

from marshmallow import Schema, fields, post_load, validates
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Regexp
from pycpfcnpj import cpfcnpj


class UserRegistrationSchema(Schema):
    doc = fields.String(required=True)
    full_name = fields.String(required=True)
    email = fields.Email(required=True)
    phone = fields.String(validate=Regexp(r'^\d{8}\d*$'), required=True)
    password = fields.String(required=True)

    @validates('doc')
    def validate_doc(self, value):
        if not cpfcnpj.validate(value):
            raise ValidationError('Invalid CNPJ/CPF')

    @post_load
    def transform(self, data: dict, **_):
        full_name = data.pop('full_name').split(' ', 1)
        data['first_name'] = full_name[0]
        data['last_name'] = full_name[1] if len(full_name) == 2 else ''

        return data


class UserActivationSchema(Schema):
    code = fields.String(required=True)

    @post_load
    def transform(self, data: dict, **_):
        data['code'] = urlsafe_b64decode(data['code']).decode('utf-8')
        return data
