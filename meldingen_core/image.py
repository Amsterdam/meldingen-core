from abc import ABCMeta, abstractmethod  # pragma: no cover
from collections.abc import AsyncIterator

from meldingen_core.malware import BaseMalwareScanner
from meldingen_core.models import Attachment


class BaseImageOptimizer(metaclass=ABCMeta):  # pragma: no cover
    @abstractmethod
    async def __call__(self, image_path: str) -> tuple[str, str]: ...


class BaseThumbnailGenerator(metaclass=ABCMeta):  # pragma: no cover
    @abstractmethod
    async def __call__(self, image_path: str) -> tuple[str, str]: ...


class BaseIngestor[T: Attachment](metaclass=ABCMeta):  # pragma: no cover
    _scan_for_malware: BaseMalwareScanner

    def __init__(self, scanner: BaseMalwareScanner):
        self._scan_for_malware = scanner

    @abstractmethod
    async def __call__(self, attachment: T, data: AsyncIterator[bytes]) -> None: ...
