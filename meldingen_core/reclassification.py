from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from meldingen_core.models import Asset, Classification, Melding

M = TypeVar("M", bound=Melding)
AS = TypeVar("AS", bound=Asset)
C = TypeVar("C", bound=Classification)


class BaseReclassification(Generic[M, C, AS], metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, melding: M, new_classification: C | None) -> None:
        """Handle reclassification side effects here, like changing the assets or removing/changing the location."""
