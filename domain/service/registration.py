import logging
import pytz
from datetime import datetime, timedelta
from typing import Optional

from domain.model import User, RequiredAction, Token
from domain.exception import (
    AuthorizationError,
    UserError,
    UserNotFound,
    UserAlreadyActiveError
)
from domain.repository import (
    ISecurityRepository,
    ITokenRepository,
    INotifier
)
from domain.util import text


class RegistrationService:
    def __init__(
        self,
        notifier: INotifier,
        security_repo: ISecurityRepository,
        token_repo: ITokenRepository
    ):
        self._notifier = notifier
        self._security_repo = security_repo
        self._token_repo = token_repo
        self._log = logging.getLogger(self.__class__.__name__)

    def import_owner(self, owner: dict):
        user = self._get_user_by_doc(owner['doc'])

        if user is None:
            self._register_owner_user(owner)
        else:
            self._update_owner_user(owner, user)

    def _get_user_by_doc(self, doc: str) -> Optional[User]:
        try:
            return self._security_repo.find_user_by_username(doc)
        except UserError:
            return None

    def _register_owner_user(self, owner: dict):
        user = User(
            id=None,
            createdTimestamp=None,
            emailVerified=False,
            enabled=False,
            doc=owner['doc'],
            username=owner['doc'],
            email=owner['email'],
            password=text.generate_phrase(20),
            firstName=owner['first_name'],
            lastName=owner['last_name'],
            defaulting=owner['defaulting'],
            groups=['producer'],
            roles=[],
            effective_roles=None,
            requiredActions=[
                RequiredAction.VERIFY_EMAIL.value,
                RequiredAction.UPDATE_PASSWORD.value
            ]
        )

        user.id = self._security_repo.create_user(user)
        self._log.debug(f'Added owner: (id={user.id}, doc={user.doc})')

    def _update_owner_user(self, owner: dict, user: User):
        user.doc = owner['doc']
        user.firstName = owner['first_name']
        user.lastName = owner['last_name']
        user.email = owner['email']
        user.defaulting = owner['defaulting']

        self._security_repo.update_user(user)
        self._log.debug(f'Updated owner: (id={user.id}, doc={user.doc})')

    def request_owner_activation(self, doc: str) -> User:
        user = self._get_user_by_doc(doc)

        if user is None:
            raise UserNotFound(f'User with doc {doc} was not found')

        if RequiredAction.VERIFY_EMAIL.value not in user.requiredActions:
            raise UserAlreadyActiveError('User email is already verified')

        code, token = Token.new(
            expire_in=timedelta(hours=1),
            action='OWNER_REGISTRATION',
            user_id=user.id
        )

        self._token_repo.add(token)
        self._log.debug(f'Added token {token._id}')

        self._notifier.send_owner_email_verification(user, code)
        self._log.debug(f'Requested owner activation with doc: {user.doc}')

        return user

    def activate_owner(self, code: str, password: str) -> User:
        token = self._token_repo.find_by_code(text.sha512(code))
        now = datetime.now(pytz.timezone('UTC'))

        if token is None:
            raise AuthorizationError('Token is invalid')

        if token.access_at is not None:
            raise AuthorizationError('Token is no longer valid')

        if now > token.expire_at:
            raise AuthorizationError('Token has expired')

        if token.action != 'OWNER_REGISTRATION':
            raise AuthorizationError('Illegal action requested for this token')

        user = self._security_repo.find_user_by_id(token.user_id)

        if user is None:
            raise UserError('User no longer exists')

        user.enabled = True
        user.emailVerified = True

        if RequiredAction.VERIFY_EMAIL.value in user.requiredActions:
            user.requiredActions.remove(RequiredAction.VERIFY_EMAIL.value)

        if RequiredAction.UPDATE_PASSWORD.value in user.requiredActions:
            user.requiredActions.remove(RequiredAction.UPDATE_PASSWORD.value)

        self._security_repo.update_user(user)
        self._security_repo.set_password(user.id, password)
        self._log.debug(f'Activated owner: (id={user.id}, doc={user.doc})')

        token.access_at = now
        self._token_repo.update(token)
        self._log.debug(
            f'Accessed token: (id={token._id}, action={token.action})'
        )

        return user

    def register_public_user(self, public: dict) -> User:
        if self._security_repo.user_exists(public['doc']):
            raise UserAlreadyActiveError(public['doc'])

        user = User(
            id=None,
            createdTimestamp=None,
            emailVerified=False,
            enabled=False,
            doc=public['doc'],
            username=public['doc'],
            email=public['email'],
            password=public['password'],
            firstName=public['first_name'],
            lastName=public['last_name'],
            defaulting=None,
            groups=['public'],
            roles=[],
            effective_roles=None,
            requiredActions=[RequiredAction.VERIFY_EMAIL.value]
        )

        user.id = self._security_repo.create_user(user)
        self._log.debug(f'Added public user: (id={user.id}, doc={user.doc})')

        code, token = Token.new(
            expire_in=timedelta(hours=1),
            action='USER_REGISTRATION',
            user_id=user.id
        )
        self._token_repo.add(token)
        self._notifier.send_email_verification(user, code)
        self._log.debug(f'Requested user activation with doc: {user.doc}')

        return user

    def activate_public_user(self, code: str) -> User:
        token = self._token_repo.find_by_code(text.sha512(code))
        now = datetime.now(pytz.timezone('UTC'))

        if token is None:
            raise AuthorizationError('Token is invalid')

        if token.access_at is not None:
            raise AuthorizationError('Token is no longer valid')

        if now > token.expire_at:
            raise AuthorizationError('Token has expired')

        if token.action != 'USER_REGISTRATION':
            raise AuthorizationError('Illegal action requested for this token')

        user = self._security_repo.find_user_by_id(token.user_id)

        if user is None:
            raise UserError('User no longer exists')

        user.enabled = True
        user.emailVerified = True

        if RequiredAction.VERIFY_EMAIL.value in user.requiredActions:
            user.requiredActions.remove(RequiredAction.VERIFY_EMAIL.value)

        self._security_repo.update_user(user)
        self._log.debug(f'Activated user: (id={user.id}, doc={user.doc})')

        token.access_at = now
        self._token_repo.update(token)
        self._log.debug(
            f'Accessed token: (id={token._id}, action={token.action})'
        )

        return user
