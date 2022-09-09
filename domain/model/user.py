from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from .model import Model


class RequiredAction(Enum):
    VERIFY_EMAIL = 'VERIFY_EMAIL'
    CONFIGURE_TOTP = 'CONFIGURE_TOTP'
    UPDATE_PASSWORD = 'UPDATE_PASSWORD'
    UPDATE_PROFILE = 'UPDATE_PROFILE'


@dataclass
class User(Model):
    id: Optional[str]
    createdTimestamp: Optional[int]
    enabled: bool
    emailVerified: bool
    username: str
    firstName: Optional[str]
    lastName: Optional[str]
    email: Optional[str]
    doc: Optional[str]
    defaulting: Optional[str]
    password: Optional[str]
    groups: List[str]
    roles: List[str]
    effective_roles: Optional[List[str]]
    requiredActions: Optional[List[str]]


@dataclass
class UserSummary(Model):
    id: str
    enabled: bool
    username: str
    firstName: Optional[str]
    lastName: Optional[str]
