from pymongo.database import Database
from typing import Optional

from domain.model import Token
from domain.repository import ITokenRepository


class TokenRepository(ITokenRepository):
    def __init__(self, db: Database):
        self._collection = db['tokens']

    def find_by_code(self, code: str) -> Optional[Token]:
        doc = self._collection.find_one({'_id': code})
        return Token.from_dict(doc) if doc else None

    def add(self, token: Token) -> Token:
        result = self._collection.insert_one(token.asdict())
        token._id = result.inserted_id
        return token

    def update(self, token: Token) -> Token:
        self._collection.replace_one({'_id': token._id}, token.asdict())
        return token
