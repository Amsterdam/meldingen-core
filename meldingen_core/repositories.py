from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from meldingen_core.models import Melding

T = TypeVar('T')
T_co = TypeVar("T_co", covariant=True)


class BaseRepository(Generic[T, T_co], metaclass=ABCMeta):
    @abstractmethod
    def add(self, obj: T) -> None:
        ...

    @abstractmethod
    def list(self, *, limit: int | None = None, offset: int | None = None) -> list[T_co]:
        ...

    @abstractmethod
    def retrieve(self, pk: int) -> T_co | None:
        ...


class BaseMeldingRepository(BaseRepository[Melding, Melding], metaclass=ABCMeta):
    """Repository for Melding."""
