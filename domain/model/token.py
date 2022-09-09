from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from domain.util import text
from .model import Model


@dataclass
class Token(Model):
    _id: str
    created_at: datetime
    expire_at: datetime
    access_at: Optional[datetime]
    user_id: str
    action: str

    @classmethod
    def new(cls, expire_in: timedelta, user_id: str, action: str):
        now = datetime.utcnow()
        secret = text.generate_phrase(255)
        token = cls(
            _id=text.sha512(secret),
            created_at=now,
            expire_at=now + expire_in,
            access_at=None,
            user_id=user_id,
            action=action
        )

        return secret, token
