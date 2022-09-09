from dataclasses import dataclass
from typing import List, Optional

from .model import Model


@dataclass
class Group(Model):
    id: Optional[str]
    name: str
    roles: List[str]


@dataclass
class GroupSummary(Model):
    id: str
    name: str
