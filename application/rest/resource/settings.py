from flask import Blueprint
from http import HTTPStatus

from domain.service import SettingsService


def get_blueprint(service: SettingsService):
    bp = Blueprint('Settings', __name__)

    @bp.post('settings/init')
    def initialize():
        service.init_settings()
        return {}, HTTPStatus.NO_CONTENT

    return bp
