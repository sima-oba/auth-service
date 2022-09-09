from http import HTTPStatus
from base64 import urlsafe_b64decode
from flask import Blueprint, request, jsonify
from marshmallow.exceptions import ValidationError

from domain.service import AccountService
from ..security import Authorization
from ...schema import (
    NewUserSchema,
    UserSchema,
    PasswordSchema,
    UsernameSchema
)


def get_blueprint(service: AccountService, auth: Authorization) -> Blueprint:
    bp = Blueprint('Users', __name__)
    user_schema = UserSchema()
    new_user_schema = NewUserSchema()
    password_schema = PasswordSchema()
    username_schema = UsernameSchema()

    def _decode_base64(_input: str) -> bytes:
        try:
            return urlsafe_b64decode(_input)
        except Exception:
            raise ValidationError('Invalid code format')

    @bp.get('/users')
    @auth.require_role()
    def search():
        _filter = request.args.to_dict()
        return jsonify(service.search_users(_filter))

    @bp.get('/users/<string:_id>')
    @auth.require_role()
    def get_by_id(_id: str):
        return jsonify(service.find_user(_id))

    @bp.post('/users')
    @auth.require_role()
    def add():
        data = new_user_schema.load(request.json)
        user_id = service.create_owner(data)
        return jsonify({'id': user_id}), HTTPStatus.CREATED

    @bp.put('/users/<string:_id>')
    @auth.require_role()
    def update(_id: str):
        data = user_schema.load(request.json)
        service.update_user(_id, data)
        return {}, HTTPStatus.NO_CONTENT

    @bp.delete('/users/<string:_id>')
    @auth.require_role()
    def remove(_id: str):
        service.remove_user(_id)
        return {}, HTTPStatus.NO_CONTENT

    @bp.post('/activation')
    def send_verify_email():
        username = username_schema.load(request.json)['username']
        service.request_verify_email(username)
        return {}, HTTPStatus.NO_CONTENT

    @bp.get('/activation/<string:code>')
    def verify_email(code: str):
        code = _decode_base64(code)
        service.verify_email(code)
        return {}, HTTPStatus.NO_CONTENT

    @bp.post('/reset_password')
    def send_reset_password():
        username = username_schema.load(request.json)['username']
        service.request_reset_password(username)
        return {}, HTTPStatus.NO_CONTENT

    @bp.put('/reset_password/<string:code>')
    def reset_password(code: str):
        code = _decode_base64(code)
        password = password_schema.load(request.json)['password']
        service.reset_password(password, code)
        return {}, HTTPStatus.NO_CONTENT

    @bp.get('/users/<string:_id>/available_roles')
    @auth.require_role()
    def get_available_roles(_id: str):
        return jsonify(service.find_available_user_roles(_id))

    @bp.get('/users/<string:_id>/available_groups')
    @auth.require_role()
    def get_available_groups(_id: str):
        return jsonify(service.find_available_user_groups(_id))

    return bp
