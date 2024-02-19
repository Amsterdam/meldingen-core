from abc import ABCMeta, abstractmethod
from collections.abc import Collection
from typing import Generic, TypeVar

from meldingen_core.models import Melding, User, Classification

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class BaseRepository(Generic[T, T_co], metaclass=ABCMeta):
    @abstractmethod
    async def save(self, obj: T) -> None:
        ...

    @abstractmethod
    async def list(self, *, limit: int | None = None, offset: int | None = None) -> Collection[T_co]:
        ...

    @abstractmethod
    async def retrieve(self, pk: int) -> T_co | None:
        ...

    @abstractmethod
    async def delete(self, pk: int) -> None:
        ...


class BaseMeldingRepository(BaseRepository[Melding, Melding], metaclass=ABCMeta):
    """Repository for Melding."""


class BaseUserRepository(BaseRepository[User, User], metaclass=ABCMeta):
    """Repository for User."""


class ClassificationRepository(BaseRepository[Classification, Classification], metaclass=ABCMeta):
    """Repository for Classification."""
