from http import HTTPStatus
from flask import Blueprint, jsonify
from marshmallow import ValidationError

from domain.exception import (
    AuthenticationError,
    AuthorizationError,
    UserError,
    UserAlreadyActiveError,
    UserNotFound,
    RoleError,
    GroupError,
    UnexpectedError
)


error_bp = Blueprint('Error handling', __name__)


def _error_response(error: Exception, status: HTTPStatus):
    return jsonify({'error': str(error)}), status


@error_bp.app_errorhandler(ValidationError)
def handle_validation_error(error: ValidationError):
    return jsonify(error.messages), HTTPStatus.BAD_REQUEST


@error_bp.app_errorhandler(AuthenticationError)
def handle_authentication_error(error: AuthenticationError):
    return _error_response(error, HTTPStatus.UNAUTHORIZED)


@error_bp.app_errorhandler(AuthorizationError)
def handle_authorization_error(error: AuthorizationError):
    return _error_response(error, HTTPStatus.FORBIDDEN)


@error_bp.app_errorhandler(UserError)
def handle_user_error(error: UserError):
    return _error_response(error, HTTPStatus.BAD_REQUEST)


@error_bp.app_errorhandler(UserNotFound)
def handle_user_not_found_error(error: UserNotFound):
    return _error_response(error, HTTPStatus.NOT_FOUND)


@error_bp.app_errorhandler(UserAlreadyActiveError)
def handle_user_already_exists_error(error: UserAlreadyActiveError):
    return _error_response(error, HTTPStatus.CONFLICT)


@error_bp.app_errorhandler(RoleError)
def handle_role_error(error: RoleError):
    return _error_response(error, HTTPStatus.BAD_REQUEST)


@error_bp.app_errorhandler(GroupError)
def handle_group_error(error: GroupError):
    return _error_response(error, HTTPStatus.BAD_REQUEST)


@error_bp.app_errorhandler(UnexpectedError)
def handle_unexpected_error(error: UnexpectedError):
    return _error_response(error, HTTPStatus.INTERNAL_SERVER_ERROR)
