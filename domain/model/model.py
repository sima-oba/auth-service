from dataclasses import dataclass, asdict
from dacite.core import from_dict


@dataclass
class Model:
    def asdict(self) -> dict:
        return asdict(self)

    def merge(self, data: dict):
        return from_dict(self.__class__, {**self.asdict(), **data})

    @classmethod
    def from_dict(cls, data):
        return from_dict(cls, data)
