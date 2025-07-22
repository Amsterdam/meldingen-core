from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Classification
from meldingen_core.repositories import BaseClassificationRepository

C = TypeVar("C", bound=Classification)


class ClassificationNotFoundException(NotFoundException): ...


class BaseClassifierAdapter(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, text: str) -> str:
        """Accepts a text as input and returns the classification name."""


class Classifier(Generic[C]):
    _adapter: BaseClassifierAdapter
    _repository: BaseClassificationRepository[C]

    def __init__(self, adapter: BaseClassifierAdapter, repository: BaseClassificationRepository[C]):
        self._adapter = adapter
        self._repository = repository

    async def __call__(self, text: str) -> C:
        name = await self._adapter(text)

        try:
            return await self._repository.find_by_name(name)
        except NotFoundException as exception:
            raise ClassificationNotFoundException() from exception
