from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from meldingen_core.models import Classification, Melding

M = TypeVar("M", bound=Melding)
C = TypeVar("C", bound=Classification)


class BaseReclassification(Generic[M, C], metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, melding: M, old_classification: C | None, new_classification: C | None) -> None:
        """Handle reclassification side effects here, like changing the assets or removing/changing the location."""


class ReclassificationNotAllowedException(Exception):
    """Raised when a melding may not be classified through the action that was called.

    Classifying a melding that already reached the backoffice discards the melder's answers and
    assets without recording why, so it is refused: such a melding may only be reclassified through
    MeldingReclassifyAction. Callers are expected to point at that route in their error response."""
