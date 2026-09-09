from abc import ABCMeta, abstractmethod

from meldingen_core.models import Melding


class BaseMeldingConfirmationMailer[T: Melding](metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, melding: T) -> None: ...


class BaseMeldingCompleteMailer[T: Melding](metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, melding: T, mail_text: str) -> None: ...
