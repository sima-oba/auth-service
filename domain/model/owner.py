from dataclasses import dataclass
from typing import Optional

from .model import Model


@dataclass
class Owner(Model):
    _id: str
    doc: str
    name: str
    email: str
    phone: str
    defaulting: Optional[str]
