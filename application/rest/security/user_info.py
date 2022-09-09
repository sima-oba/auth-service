from dataclasses import dataclass
from typing import List


@dataclass
class UserInfo:
    username: str
    active: bool
    email_verified: bool
    roles: List[str]
