from abc import ABC, abstractmethod
from typing import List

from ..model import User, UserSummary, Group, GroupSummary, Role, Jwt


class ISecurityRepository(ABC):
    @abstractmethod
    def login(self, username: str, password: str) -> Jwt:
        pass

    @abstractmethod
    def logout(self, refresh_token: str):
        pass

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> Jwt:
        pass

    @abstractmethod
    def introspect_token(self, access_token: str) -> Jwt:
        pass

    @abstractmethod
    def search_users(self, _filter: dict) -> List[UserSummary]:
        pass

    @abstractmethod
    def user_exists(self, username: str) -> bool:
        pass

    @abstractmethod
    def find_user_by_id(self, _id: str) -> User:
        pass

    @abstractmethod
    def find_user_by_username(self, username: str) -> User:
        pass

    @abstractmethod
    def create_user(self, user: User) -> str:
        pass

    @abstractmethod
    def update_user(self, user: User):
        pass

    @abstractmethod
    def remove_user(self, _id: str):
        pass

    @abstractmethod
    def set_password(self, user_id: str, password: str):
        pass

    @abstractmethod
    def find_all_groups(self) -> List[GroupSummary]:
        pass

    @abstractmethod
    def find_group_by_id(self, _id: str) -> Group:
        pass

    @abstractmethod
    def create_group(self, group: Group) -> str:
        pass

    @abstractmethod
    def update_group(self, group: Group):
        pass

    @abstractmethod
    def remove_group(self, _id: str):
        pass

    @abstractmethod
    def find_all_roles(self) -> List[Role]:
        pass

    @abstractmethod
    def find_available_user_groups(_id: str) -> List[str]:
        pass

    @abstractmethod
    def find_available_user_roles(self, user_id: str) -> List[str]:
        pass

    @abstractmethod
    def find_available_group_roles(self, group_id: str) -> List[str]:
        pass

    @abstractmethod
    def create_role(self, role_name: str):
        pass
