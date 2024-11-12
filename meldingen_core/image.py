from abc import ABCMeta, abstractmethod  # pragma: no cover
from typing import AsyncIterator, Generic, TypeVar

from meldingen_core.models import Attachment


class BaseImageOptimizer(metaclass=ABCMeta):  # pragma: no cover
    @abstractmethod
    async def __call__(self, image_path: str) -> str: ...


class BaseThumbnailGenerator(metaclass=ABCMeta):  # pragma: no cover
    @abstractmethod
    async def __call__(self, image_path: str) -> str: ...


T = TypeVar("T", bound=Attachment)


class BaseIngestor(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, attachment: T, data: AsyncIterator[bytes]) -> None: ...
