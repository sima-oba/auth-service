from flask import Blueprint, jsonify

from domain.service import AccountService


def get_blueprint(service: AccountService) -> Blueprint:
    bp = Blueprint('Roles', __name__)

    @bp.get('/roles')
    def get_all():
        return jsonify(service.find_all_roles())

    return bp
