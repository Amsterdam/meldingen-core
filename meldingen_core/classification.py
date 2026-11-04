from abc import ABCMeta, abstractmethod

from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Classification
from meldingen_core.repositories import BaseClassificationRepository


class ClassificationNotFoundException(NotFoundException): ...


class ClassificationAdapterFailedException(Exception): ...


class BaseClassifierAdapter(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, text: str) -> str | None:
        """Accepts a text as input and returns the classification name."""


class Classifier[C: Classification]:
    _adapter: BaseClassifierAdapter
    _repository: BaseClassificationRepository[C]

    def __init__(
        self,
        adapter: BaseClassifierAdapter,
        repository: BaseClassificationRepository[C],
    ):
        self._adapter = adapter
        self._repository = repository

    async def __call__(self, text: str) -> C:
        name = None
        try:
            name = await self._adapter(text)
        except Exception as exception:
            raise ClassificationAdapterFailedException(str(exception)) from exception

        if name is None:
            raise ClassificationNotFoundException("Adapter returned None as classification")

        try:
            return await self._repository.find_by_name(name)
        except NotFoundException as exception:
            raise ClassificationNotFoundException(f"Classification '{name}' not found in repository") from exception
