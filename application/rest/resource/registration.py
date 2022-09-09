from flask import Blueprint, request, jsonify

from application.schema import (
    NewOwnerActivationSchema,
    OwnerActivationSchema,
    UserRegistrationSchema,
    UserActivationSchema
)
from domain.service import RegistrationService


def get_blueprint(service: RegistrationService) -> Blueprint:
    bp = Blueprint('Registration', __name__)

    user_registration_schema = UserRegistrationSchema()
    user_activation_schema = UserActivationSchema()

    new_activation_schema = NewOwnerActivationSchema()
    activation_schema = OwnerActivationSchema()

    @bp.post('/registration/owners')
    def request_owner_activation():
        data = new_activation_schema.load(request.json)
        user = service.request_owner_activation(data)

        return jsonify({'email': user.email})

    @bp.post('/registration/owners/activation')
    def activate_owner():
        data = activation_schema.load(request.json)
        user = service.activate_owner(data['code'], data['password'])

        return jsonify(user)

    @bp.post('/registration/public')
    def register_public_user():
        data = user_registration_schema.load(request.json)
        user = service.register_public_user(data)

        return jsonify({'email': user.email})

    @bp.post('/registration/public/activation')
    def activate_public_user():
        data = user_activation_schema.load(request.json)
        user = service.activate_public_user(data['code'])

        return jsonify(user)

    return bp
