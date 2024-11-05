from abc import ABCMeta, abstractmethod


class BaseImageOptimizer(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, image_path: str) -> str: ...
