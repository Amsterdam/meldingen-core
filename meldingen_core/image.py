from abc import ABCMeta, abstractmethod  # pragma: no cover


class BaseImageOptimizer(metaclass=ABCMeta):  # pragma: no cover
    @abstractmethod
    async def __call__(self, image_path: str) -> str: ...
