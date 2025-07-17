from abc import ABCMeta, abstractmethod

from meldingen_core.models import Classification, Melding


class BaseReclassification(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, melding: Melding, new_classification: Classification | None) -> None:
        """Handle reclassification side effects here, like changing the assets or removing/changing the location."""
