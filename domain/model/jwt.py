from dataclasses import dataclass
from typing import Optional

from .model import Model
from .user import User


@dataclass
class Jwt(Model):
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: str
    token_type: str
    session_state: str
    scope: str
    user: Optional[User] = None
