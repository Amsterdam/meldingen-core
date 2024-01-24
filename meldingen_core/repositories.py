from abc import ABCMeta, abstractmethod

from meldingen_core.models import Melding


class BaseMeldingRepository(metaclass=ABCMeta):
    """Repository for Melding."""

    @abstractmethod
    def add(self, melding: Melding) -> None:
        ...
