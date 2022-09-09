from flask import Blueprint, request, jsonify
from http import HTTPStatus

from domain.service import AccountService
from ...schema import GroupSchema


def get_blueprint(service: AccountService) -> Blueprint:
    bp = Blueprint('Groups', __name__)
    schema = GroupSchema()

    @bp.get('/groups')
    def get_all():
        return jsonify(service.find_all_groups())

    @bp.get('/groups/<string:_id>')
    def get_by_id(_id: str):
        return jsonify(service.find_group(_id))

    @bp.post('/groups')
    def add():
        data = schema.load(request.json)
        group_id = service.create_group(data)
        return {'id': group_id}, HTTPStatus.CREATED

    @bp.put('/groups/<string:_id>')
    def update(_id: str):
        data = schema.load(request.json)
        service.update_group(_id, data)
        return {}, HTTPStatus.NO_CONTENT

    @bp.delete('/groups/<string:_id>')
    def remove(_id: str):
        service.remove_group(_id)
        return {}, HTTPStatus.NO_CONTENT

    @bp.get('/groups/<string:_id>/available_roles')
    def get_available_roles(_id: str):
        return jsonify(service.find_available_group_roles(_id))

    return bp
