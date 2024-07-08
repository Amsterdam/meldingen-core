from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from meldingen_core.models import Attachment, Melding

A = TypeVar("A", bound=Attachment)


class BaseAttachmentFactory(Generic[A], metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, original_filename: str, melding: Melding) -> A: ...
