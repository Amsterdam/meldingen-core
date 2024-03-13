from abc import ABCMeta, abstractmethod


class BaseClassifierAdapter(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, text: str) -> str:
        """Accepts a text as input and returns the classification name."""


class Classifier:
    _adapter: BaseClassifierAdapter

    def __init__(self, adapter: BaseClassifierAdapter):
        self._adapter = adapter

    async def __call__(self, text: str) -> str:
        return await self._adapter(text)
