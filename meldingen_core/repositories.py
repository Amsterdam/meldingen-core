from abc import ABCMeta, abstractmethod

from meldingen_core.models import Melding


class BaseMeldingRepository(metaclass=ABCMeta):
    """Repository for Melding."""

    @abstractmethod
    def add(self, melding: Melding) -> None:
        ...

    @abstractmethod
    def list(self, *, limit: int | None = None, offset: int | None = None) -> list[Melding]:
        ...

    @abstractmethod
    def retrieve(self, pk: int) -> Melding | None:
        ...
