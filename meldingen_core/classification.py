from abc import ABCMeta, abstractmethod

from meldingen_core.models import Classification
from meldingen_core.repositories import BaseClassificationRepository


class BaseClassifierAdapter(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, text: str) -> str:
        """Accepts a text as input and returns the classification name."""


class Classifier:
    _adapter: BaseClassifierAdapter
    _repository: BaseClassificationRepository

    def __init__(self, adapter: BaseClassifierAdapter, repository: BaseClassificationRepository):
        self._adapter = adapter
        self._repository = repository

    async def __call__(self, text: str) -> Classification:
        name = await self._adapter(text)

        return await self._repository.find_by_name(name)
