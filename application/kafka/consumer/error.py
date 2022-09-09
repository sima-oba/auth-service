import logging
from functools import wraps
from marshmallow import ValidationError

from domain.exception import (
    AuthenticationError,
    AuthorizationError,
    GroupError,
    RoleError,
    UnexpectedError,
    UserError
)
from .base import BaseConsumer


_log = logging.getLogger(__name__)
_exceptions = (
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    GroupError,
    RoleError,
    UnexpectedError,
    UserError
)


def _is_process_method(method) -> bool:
    return hasattr(method, '__name__') and method.__name__ == 'process'


def _is_consumer_instance(args) -> bool:
    return len(args) > 0 and isinstance(args[0], BaseConsumer)


def error_handler(method):

    @wraps(method)
    def wrapper(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except _exceptions as e:
            if _is_consumer_instance(args) and _is_process_method(method):
                msg = args[1]
                _log.exception(
                    'Error occured while processing message: '
                    f'{msg.topic()} - {msg.key()} - {msg.value()}'
                )
            else:
                _log.exception(e)

    return wrapper
