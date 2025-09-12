from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from meldingen_core.models import Asset, AssetType, Attachment, Melding

A = TypeVar("A", bound=Attachment)
M = TypeVar("M", bound=Melding)


class BaseAttachmentFactory(Generic[A, M], metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, original_filename: str, melding: M, media_type: str) -> A: ...


AS = TypeVar("AS", bound=Asset)
AT = TypeVar("AT", bound=AssetType)


class BaseAssetFactory(Generic[AS, AT, M], metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, external_id: str, asset_type: AT, melding: M) -> AS: ...
