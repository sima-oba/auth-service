from dataclasses import dataclass

from .model import Model


@dataclass
class Role(Model):
    id: str
    name: str
