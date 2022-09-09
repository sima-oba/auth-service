from abc import ABC, abstractmethod
from typing import Optional

from domain.model import Token


class ITokenRepository(ABC):
    @abstractmethod
    def find_by_code(self, code: str) -> Optional[Token]:
        pass

    @abstractmethod
    def add(self, token: Token) -> Token:
        pass

    @abstractmethod
    def update(self, token: Token) -> Token:
        pass
