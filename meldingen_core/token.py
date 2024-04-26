from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Generic, TypeVar

from meldingen_core.models import Melding

T = TypeVar("T", bound=Melding)


class BaseTokenGenerator(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self) -> str:
        """Generates and returns token"""


class TokenException(Exception): ...


class InvalidTokenException(TokenException): ...


class TokenExpiredException(TokenException): ...


class TokenVerifier(Generic[T]):
    def __call__(self, melding: T, token: str) -> None:
        if token != melding.token:
            raise InvalidTokenException()

        if melding.token_expires is not None and melding.token_expires < datetime.now():
            raise TokenExpiredException()
