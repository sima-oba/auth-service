import random
import string
import hashlib
from typing import Union


def generate_phrase(length: int) -> str:
    choices = random.choices(
        string.ascii_uppercase +
        string.ascii_lowercase +
        string.digits +
        string.punctuation,
        k=length
    )

    return ''.join(choices)


def sha512(code: Union[str, bytes]) -> str:
    if isinstance(code, str):
        code = code.encode('ascii')

    return hashlib.sha512(code).hexdigest()
