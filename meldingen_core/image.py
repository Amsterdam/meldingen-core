from abc import ABCMeta, abstractmethod  # pragma: no cover

from meldingen_core.models import Attachment


class BaseImageOptimizer(metaclass=ABCMeta):  # pragma: no cover
    @abstractmethod
    async def __call__(self, image_path: str) -> str: ...


class BaseThumbnailGenerator(metaclass=ABCMeta):  # pragma: no cover
    @abstractmethod
    async def __call__(self, image_path: str) -> str: ...


class BaseIngestor(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, attachment: Attachment) -> None: ...
