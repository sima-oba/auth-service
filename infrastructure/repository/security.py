import json
from http import HTTPStatus
from typing import List
from keycloak.exceptions import KeycloakGetError, KeycloakAuthenticationError

from domain.model import (
    User,
    UserSummary,
    Group,
    GroupSummary,
    Role,
    Jwt
)
from domain.exception import (
    AuthenticationError,
    AuthorizationError,
    RoleError,
    UnexpectedError,
    UserError,
    GroupError
)
from domain.repository import ISecurityRepository
from ..keycloak import Keycloak


class SecurityRepository(ISecurityRepository):
    def __init__(self, keycloak: Keycloak):
        self._admin = keycloak.cli_admin
        self._openid = keycloak.cli_openid

    def _get_error_message(self, error: KeycloakGetError) -> str:
        return json.loads(error.response_body)['error_description']

    def login(self, username: str, password: str) -> Jwt:
        try:
            token = self._openid.token(username, password)
            return Jwt.from_dict(token)
        except KeycloakAuthenticationError:
            raise AuthenticationError('Invalid credentials')
        except KeycloakGetError as error:
            raise AuthorizationError(self._get_error_message(error))

    def logout(self, refresh_token: str):
        try:
            self._openid.logout(refresh_token=refresh_token)
        except KeycloakGetError as error:
            raise AuthorizationError(self._get_error_message(error))

    def refresh_token(self, refresh_token: str) -> Jwt:
        try:
            token = self._openid.refresh_token(refresh_token)
            return Jwt.from_dict(token)
        except KeycloakGetError as error:
            raise AuthorizationError(self._get_error_message(error))

    def introspect_token(self, access_token: str) -> dict:
        return self._openid.introspect(access_token)

    def _get_roles_by_name(self, role_names: List[str]) -> List[dict]:
        roles = []

        for name in role_names:
            try:
                roles.append(self._admin.get_realm_role(name))
            except KeycloakGetError:
                raise RoleError(f'Role {name} does not exist')

        return roles

    def _get_groups_by_name(self, group_names: List[str]) -> List[dict]:
        groups = []

        for name in group_names:
            group = self._admin.get_group_by_path('/' + name)

            if group is None:
                raise GroupError(f'Group {name} does not exist')

            groups.append(group)

        return groups

    def _get_user_details(self, user_repr: dict) -> User:
        _id = user_repr['id']

        attribs = {
            key: value[0]
            for key, value in user_repr.pop('attributes', {}).items()
        }

        groups = [
            group['name']
            for group in self._admin.get_user_groups(_id)
        ]

        roles = [
            role['name']
            for role in self._admin.get_realm_roles_of_user(_id)
        ]

        roles_path = f'/admin/realms/{self._admin.realm_name}' \
                     f'/users/{_id}/role-mappings/realm/composite'

        effective_roles = [
            role['name']
            for role in self._admin.raw_get(roles_path).json()
        ]

        return User.from_dict({
            **user_repr,
            **attribs,
            'groups': groups,
            'roles': roles,
            'effective_roles': effective_roles
        })

    def search_users(self, _filter: dict) -> List[UserSummary]:
        summary = self._admin.get_users(_filter)
        return [UserSummary.from_dict(user) for user in summary]

    def user_exists(self, username: str) -> bool:
        results = self._admin.get_users({'username': username})
        return len(results) > 0

    def find_user_by_id(self, _id: str) -> User:
        try:
            result = self._admin.get_user(_id)
            return self._get_user_details(result)
        except KeycloakGetError as err:
            if err.response_code == HTTPStatus.NOT_FOUND:
                raise UserError(f'User with id {_id} not found')
            raise UnexpectedError(err)

    def find_user_by_username(self, username: str) -> User:
        results = self._admin.get_users({'username': username})

        if len(results) == 0:
            raise UserError(f'User {username} not found')

        return self._get_user_details(results[0])

    def create_user(self, user: User) -> str:
        user_groups = self._get_groups_by_name(user.groups)
        user_roles = self._get_roles_by_name(user.roles)
        user_repr = {
            'username': user.username,
            'email': user.email,
            'emailVerified': user.emailVerified,
            'enabled': user.enabled,
            'firstName': user.firstName,
            'lastName': user.lastName,
            'credentials': [{
                'type': 'password',
                'value': user.password
            }],
            'attributes': {
                'doc': user.doc,
                'defaulting': user.defaulting
            },
            'requiredActions': user.requiredActions
        }

        try:
            user_id = self._admin.create_user(user_repr, False)
        except KeycloakGetError as err:
            if err.response_code == HTTPStatus.CONFLICT:
                raise UserError(f'User {user.username} already exists')
            raise UnexpectedError(err)

        for group in user_groups:
            self._admin.group_user_add(user_id, group['id'])

        if user_roles:
            self._admin.assign_realm_roles(user_id, user_roles)

        return user_id

    def update_user(self, user: User):
        try:
            self._admin.get_user(user.id)
        except KeycloakGetError:
            raise UserError(f'User with id {user.id} not found')

        current_groups = self._admin.get_user_groups(user.id)
        new_groups = self._get_groups_by_name(user.groups)

        current_roles = self._admin.get_realm_roles_of_user(user.id)
        new_roles = self._get_roles_by_name(user.roles)

        user_repr = {
            'username': user.username,
            'email': user.email,
            'emailVerified': user.emailVerified,
            'enabled': user.enabled,
            'firstName': user.firstName,
            'lastName': user.lastName,
            'attributes': {
                'doc': user.doc,
                'defaulting': user.defaulting
            },
            'requiredActions': user.requiredActions
        }

        self._admin.update_user(user.id, user_repr)

        for group in current_groups:
            self._admin.group_user_remove(user.id, group['id'])

        for group in new_groups:
            self._admin.group_user_add(user.id, group['id'])

        if current_roles:
            self._admin.delete_user_realm_role(user.id, current_roles)

        if new_roles:
            self._admin.assign_realm_roles(user.id, new_roles)

    def remove_user(self, _id: str):
        try:
            self._admin.delete_user(_id)
        except KeycloakGetError:
            raise UserError(f'User with id {_id} not found')

    def set_password(self, user_id: str, new_password: str):
        try:
            self._admin.set_user_password(user_id, new_password, False)
        except KeycloakGetError:
            raise UserError(f'User with id {user_id} not found')

    def find_all_groups(self) -> List[GroupSummary]:
        return [
            GroupSummary.from_dict(group)
            for group in self._admin.get_groups()
        ]

    def find_group_by_id(self, _id: str) -> Group:
        try:
            group = self._admin.get_group(_id)
            roles = [
                role['name']
                for role in self._admin.get_group_realm_roles(_id)
            ]

            return Group.from_dict({**group, 'roles': roles})
        except KeycloakGetError:
            raise GroupError(f'Group with id {_id} not found')

    def create_group(self, group: Group) -> str:
        roles = self._get_roles_by_name(group.roles + ['default-roles-master'])

        try:
            self._admin.create_group({'name': group.name}, skip_exists=True)
        except KeycloakGetError as err:
            if err.response_code == HTTPStatus.CONFLICT:
                raise GroupError(f'Group {group.name} already exists')
            raise UnexpectedError(err)

        group_id = self._admin.get_group_by_path(f'/{group.name}')['id']

        if roles:
            self._admin.assign_group_realm_roles(group_id, roles)

        return group_id

    def update_group(self, group: Group):
        try:
            self._admin.get_group(group.id)
        except KeycloakGetError:
            raise GroupError(f'Group with id {group.id} not found')

        current_roles = self._admin.get_group_realm_roles(group.id)
        new_roles = self._get_roles_by_name(group.roles)

        try:
            self._admin.update_group(group.id, {'name': group.name})
        except KeycloakGetError as err:
            if err.response_code == HTTPStatus.CONFLICT:
                raise GroupError(f'Group {group.name} already exists')
            raise UnexpectedError(err)

        if current_roles:
            self._admin.delete_group_realm_roles(group.id, current_roles)

        if new_roles:
            self._admin.assign_group_realm_roles(group.id, new_roles)

    def remove_group(self, _id) -> dict:
        try:
            self._admin.delete_group(_id)
        except KeycloakGetError:
            raise GroupError(f'Group with id {_id} not found')

    def find_available_user_groups(self, user_id: str) -> List[str]:
        try:
            user_groups = {
                group['name']
                for group in self._admin.get_user_groups(user_id)
            }

            all_groups = {
                group['name']
                for group in self._admin.get_groups()
            }

            return list(all_groups - user_groups)
        except KeycloakGetError:
            raise UserError(f'User with id {user_id} not found')

    def find_all_roles(self) -> List[Role]:
        return [
            Role.from_dict(role)
            for role in self._admin.get_realm_roles()
        ]

    def find_available_user_roles(self, user_id) -> List[str]:
        path = f'/admin/realms/{self._admin.realm_name}' \
               f'/users/{user_id}/role-mappings/realm/available'

        response = self._admin.raw_get(path)

        if not response.ok:
            raise UserError(f'User with id {user_id} not found')

        return {role['name'] for role in response.json()}

    def find_available_group_roles(self, group_id: str) -> List[str]:
        path = f'/admin/realms/{self._admin.realm_name}' \
               f'/groups/{group_id}/role-mappings/realm/available'

        response = self._admin.raw_get(path)

        if not response.ok:
            raise GroupError(f'Group with id {group_id} not found')

        return {role['name'] for role in response.json()}

    def create_role(self, role_name: str):
        self._admin.create_realm_role({'name': role_name}, skip_exists=True)
