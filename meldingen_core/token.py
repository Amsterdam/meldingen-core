from abc import ABCMeta, abstractmethod


class BaseTokenGenerator(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self) -> str:
        """Generates and returns token"""
