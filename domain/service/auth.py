from domain.exception import AuthorizationError
from ..model import Jwt, User
from ..repository import ISecurityRepository


class AuthService:
    def __init__(self, auth_repo: ISecurityRepository):
        self._auth_repo = auth_repo

    def login(self, username: str, password: str) -> Jwt:
        jwt = self._auth_repo.login(username, password)
        jwt.user = self._auth_repo.find_user_by_username(username)
        self._check_user_pre_conditions(jwt.user)

        return jwt

    def logout(self, refresh_token: str):
        self._auth_repo.logout(refresh_token)

    def refresh_token(self, refresh_token: str) -> Jwt:
        return self._auth_repo.refresh_token(refresh_token)

    def introspect_token(self, access_token) -> str:
        return self._auth_repo.introspect_token(access_token)

    def _check_user_pre_conditions(self, user: User):
        if user.defaulting == 'true':
            raise AuthorizationError(
                f'User {user.username} has outstanding debts'
            )
