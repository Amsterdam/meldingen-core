from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from meldingen_core.models import Classification, Melding

M = TypeVar("M", bound=Melding)
C = TypeVar("C", bound=Classification)


class BaseReclassification(Generic[M, C], metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, melding: M, old_classification: C | None, new_classification: C | None) -> M:
        """Handle reclassification side effects here, like changing the assets or removing/changing the location."""
