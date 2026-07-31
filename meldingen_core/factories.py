from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from meldingen_core.models import Asset, AssetType, Attachment, Melding, Note, User

A = TypeVar("A", bound=Attachment)
M = TypeVar("M", bound=Melding)
U = TypeVar("U", bound=User)


class BaseAttachmentFactory(Generic[A, M, U], metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, original_filename: str, melding: M, media_type: str, user: U | None) -> A: ...


AS = TypeVar("AS", bound=Asset)
AT = TypeVar("AT", bound=AssetType)


class BaseAssetFactory(Generic[AS, AT, M], metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, external_id: str, asset_type: AT, melding: M, label: str, subtype: str) -> AS: ...


N = TypeVar("N", bound=Note)


class BaseNoteFactory(Generic[N, M, U], metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, text: str, melding: M, user: U) -> N: ...
