from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Generic, TypeVar

from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository

T = TypeVar("T", bound=Melding)
T_co = TypeVar("T_co", bound=Melding, covariant=True)


class BaseTokenGenerator(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self) -> str:
        """Generates and returns token"""


class TokenException(Exception): ...


class InvalidTokenException(TokenException): ...


class TokenExpiredException(TokenException): ...


class TokenVerifier(Generic[T, T_co]):
    _repository: BaseMeldingRepository[T, T_co]

    def __init__(self, repository: BaseMeldingRepository[T, T_co]):
        self._repository = repository

    async def __call__(self, melding_id: int, token: str) -> T:
        melding = await self._repository.retrieve(melding_id)
        if melding is None:
            raise NotFoundException("Melding not found")

        if token != melding.token:
            raise InvalidTokenException()

        if melding.token_expires is not None and melding.token_expires < datetime.now():
            raise TokenExpiredException()

        return melding
