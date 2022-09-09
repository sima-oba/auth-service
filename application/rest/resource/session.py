from http import HTTPStatus
from flask import Blueprint, request, jsonify

from domain.service import AuthService
from ...schema import LoginSchema, TokenSchema


def get_blueprint(service: AuthService) -> Blueprint:
    bp = Blueprint('Auth', __name__)
    login_schema = LoginSchema()
    token_schema = TokenSchema()

    @bp.post('/session/login')
    def login():
        data = login_schema.load(request.json)
        token = service.login(**data)
        return jsonify(token)

    @bp.post('/session/logout')
    def logout():
        token = token_schema.load(request.json)['token']
        service.logout(token)
        return {}, HTTPStatus.NO_CONTENT

    @bp.post('/session/refresh')
    def refresh():
        token = token_schema.load(request.json)['token']
        token = service.refresh_token(token)
        return jsonify(token)

    @bp.post('/session/introspect')
    def introspect():
        token = token_schema.load(request.json)['token']
        return service.introspect_token(token)

    return bp
