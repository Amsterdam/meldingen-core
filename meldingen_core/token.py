import datetime as dt
from abc import ABCMeta, abstractmethod

from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository


class BaseTokenGenerator(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self) -> str:
        """Generates and returns token"""


class TokenException(Exception): ...


class InvalidTokenException(TokenException): ...


class TokenExpiredException(TokenException): ...


class InvalidStateException(TokenException): ...


class TokenVerifier[T: Melding]:
    _repository: BaseMeldingRepository[T]

    def __init__(self, repository: BaseMeldingRepository[T]):
        self._repository = repository

    async def __call__(self, melding_id: int, token: str) -> T:
        from meldingen_core.repository_helpers import retrieve_or_raise_not_found

        melding = await retrieve_or_raise_not_found(self._repository, melding_id)

        if token != melding.token:
            raise InvalidTokenException()

        if melding.token_expires is not None and melding.token_expires < dt.datetime.now(tz=dt.UTC):
            raise TokenExpiredException()

        return melding


class BaseTokenInvalidator[T: Melding](metaclass=ABCMeta):
    async def __call__(self, melding: T) -> T:
        if not melding.state in self.allowed_states:
            raise InvalidStateException()

        melding.token = None

        return melding

    @property
    @abstractmethod
    def allowed_states(self) -> list[str]:
        return []
