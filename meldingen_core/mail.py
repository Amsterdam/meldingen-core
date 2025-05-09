from abc import ABCMeta, abstractmethod
from typing import TypeVar

from meldingen_core.models import Melding

T = TypeVar("T", bound=Melding)


class BaseMeldingConfirmationMailer(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, melding: T) -> None: ...
