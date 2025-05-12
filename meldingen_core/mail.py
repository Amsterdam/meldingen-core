from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from meldingen_core.models import Melding

T = TypeVar("T", bound=Melding)


class BaseMeldingConfirmationMailer(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, melding: T) -> None: ...
