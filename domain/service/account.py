import logging
import random
import string
from datetime import datetime, timedelta
from hashlib import sha512
from typing import List, Union
from uuid import uuid4

from ..model import (
    User,
    UserSummary,
    Group,
    GroupSummary,
    Role,
    Token,
    Owner
)
from ..exception import AuthorizationError, UserError
from ..repository import (
    ISecurityRepository,
    ITokenRepository,
    INotifier,
    IProtocolPublisher
)


_log = logging.getLogger(__name__)


class AccountService:
    def __init__(
        self,
        security: ISecurityRepository,
        tokens: ITokenRepository,
        notification_pub: INotifier,
        protocol_pub: IProtocolPublisher
    ):
        self._security = security
        self._tokens = tokens
        self._notification_pub = notification_pub
        self._protocol_pub = protocol_pub

    def _hash(self, code: Union[str, bytes]) -> str:
        if isinstance(code, str):
            code = code.encode('ascii')

        return sha512(code).hexdigest()

    def _add_token(self, user_id: str, expire: timedelta, action: str) -> str:
        code = ''.join(random.choices(
            string.ascii_uppercase +
            string.ascii_lowercase +
            string.digits +
            string.punctuation,
            k=255
        ))
        now = datetime.utcnow()
        token = Token(
            _id=self._hash(code),
            created_at=now,
            expire_at=now + expire,
            access_at=None,
            user_id=user_id,
            action=action
        )

        self._tokens.add(token)
        return code

    def _get_token(self, code: str, action: str) -> Token:
        token = self._tokens.find_by_code(self._hash(code))

        if token is None:
            raise AuthorizationError('Invalid token')

        if token.access_at or token.expire_at < datetime.now().astimezone():
            raise AuthorizationError('Token is no longer valid')

        if token.action != action:
            raise AuthorizationError('Illegal requested action')

        return token

    def search_users(self, _filter: dict) -> List[UserSummary]:
        return self._security.search_users(_filter)

    def find_user(self, _id: str) -> User:
        return self._security.find_user_by_id(_id)

    def create_owner(self, data: dict) -> str:
        owner = Owner(
            _id=str(uuid4()),
            doc=data['doc'],
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            defaulting=None
        )

        self._protocol_pub.send_new_owner(owner)
        _log.debug(f'New owner protocol sent {owner._id}')

        return owner._id

    def update_user(self, _id: str, data: dict):
        user = self._security.find_user_by_id(_id)
        user = user.merge(data)
        self._security.update_user(user)
        _log.debug(f'Updated user {_id}')

    def remove_user(self, _id: str):
        self._security.remove_user(_id)
        _log.debug(f'Removed user {_id}')

    def find_available_user_groups(self, user_id: str) -> List[str]:
        return self._security.find_available_user_groups(user_id)

    def find_available_user_roles(self, user_id: str) -> List[Role]:
        return self._security.find_available_user_roles(user_id)

    def find_all_groups(self) -> List[GroupSummary]:
        return self._security.find_all_groups()

    def find_group(self, _id) -> Group:
        return self._security.find_group_by_id(_id)

    def create_group(self, data: dict) -> str:
        group_id = self._security.create_group(Group(id=None, **data))
        _log.debug(f'Created group {group_id}')

        return group_id

    def update_group(self, _id: str, data: dict):
        self._security.update_group(Group(id=_id, **data))
        _log.debug('Updated group {_id}')

    def remove_group(self, _id: str):
        self._security.remove_group(_id)
        _log.debug(f'Removed group {_id}')

    def find_available_group_roles(self, group_id: str) -> List[Role]:
        return self._security.find_available_group_roles(group_id)

    def find_all_roles(self) -> List[Role]:
        return self._security.find_all_roles()

    def import_owner(self, data: dict) -> str:
        user = self._security.find_user_by_username(data['email'])

        if user is None:
            user = User(
                id=None,
                createdTimestamp=None,
                emailVerified=True,
                enabled=False,
                doc=data['doc'],
                username=data['email'],
                password='00000',
                firstName=data['first_name'],
                lastName=data['last_name'],
                defaulting=data['defaulting'],
                groups=[],
                roles=[],
                effective_roles=None,
                requiredActions=['UPDATE_PASSWORD']
            )

            user.id = self._security.create_user(user)
            expire_in = timedelta(days=365)
            code = self._add_token(user.id, expire_in, 'UPDATE_PASSWORD')
            self._notification_pub.send_reset_password(user, code)

            _log.debug(f'Imported user {user.id} with pending password')
        else:
            user.doc = data['doc']
            user.firstName = data['first_name']
            user.lastName = data['last_name']
            user.defaulting = data['defaulting']
            self._security.update_user(user)

            _log.debug(f'Updated user {user.id}')

        return user.id

    def request_verify_email(self, username: str):
        user = self._security.find_user_by_username(username)

        if user.emailVerified and 'VERIFY_EMAIL' not in user.requiredActions:
            raise UserError(f'User {user.username} has already been verified')

        expire_in = timedelta(minutes=30)
        code = self._add_token(user.id, expire_in, 'VERIFY_EMAIL')
        self._notification_pub.send_email_verification(user, code)
        _log.debug(f'Email verification sent to {username}')

    def verify_email(self, code: bytes):
        token = self._get_token(code, 'VERIFY_EMAIL')
        token.access_at = datetime.utcnow()
        self._tokens.update(token)

        user = self._security.find_user_by_id(token.user_id)
        user.emailVerified = True

        if 'VERIFY_EMAIL' in user.requiredActions:
            user.requiredActions.remove('VERIFY_EMAIL')

        self._security.update_user(user)
        _log.debug(f'User\'s email {user.username} verified')

    def request_reset_password(self, username: str):
        user = self._security.find_user_by_username(username)
        expire_in = timedelta(minutes=30)
        code = self._add_token(user.id, expire_in, 'UPDATE_PASSWORD')
        self._notification_pub.send_reset_password(user, code)
        _log.debug(f'Sent reset password to {username}')

    def reset_password(self, password: str, code: bytes):
        token = self._get_token(code, 'UPDATE_PASSWORD')
        token.access_at = datetime.utcnow()
        self._tokens.update(token)
        self._security.set_password(token.user_id, password)
        _log.debug(f'User {token.user_id} redefined the password')
