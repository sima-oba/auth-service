from base64 import urlsafe_b64decode
from marshmallow import Schema, fields, validates, post_load
from marshmallow.exceptions import ValidationError
from pycpfcnpj import cpfcnpj


class NewOwnerActivationSchema(Schema):
    doc = fields.String(required=True)

    @validates('doc')
    def validate_doc(self, value):
        if not cpfcnpj.validate(value):
            raise ValidationError('Invalid CNPJ or CPF')

    @post_load
    def format(self, data: dict, **_) -> str:
        return data['doc']


class OwnerActivationSchema(Schema):
    code = fields.String(required=True)
    password = fields.String(required=True)

    @post_load
    def format(self, data: dict, **_):
        data['code'] = urlsafe_b64decode(data['code']).decode('utf-8')
        return data
