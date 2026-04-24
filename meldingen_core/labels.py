from abc import ABCMeta, abstractmethod
from typing import TypeVar

from meldingen_core.models import Label, Melding
from meldingen_core.repositories import BaseLabelRepository

T = TypeVar("T", bound=Melding)


class InvalidLabelException(Exception): ...


class BaseLabelReplacer(metaclass=ABCMeta):
    label_repository: BaseLabelRepository[Label]

    def __init__(self, label_repository: BaseLabelRepository[Label]) -> None:
        self._label_repository = label_repository

    @abstractmethod
    async def __call__(self, melding: T, label_ids: list[int]) -> T:
        """Abstraction to overwrite a melding's current labels with a new set. Will return the updated melding if they can all be found. Raises InvalidLabelException if not."""
