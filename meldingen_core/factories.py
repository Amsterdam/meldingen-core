from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from meldingen_core.models import Attachment, Melding

A = TypeVar("A", bound=Attachment)
M = TypeVar("M", bound=Melding)


class BaseAttachmentFactory(Generic[A, M], metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, original_filename: str, melding: M) -> A: ...
