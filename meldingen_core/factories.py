from abc import ABCMeta, abstractmethod

from meldingen_core.models import Asset, AssetType, Attachment, Melding, Note, User


class BaseAttachmentFactory[A: Attachment, M: Melding, U: User | None](metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, original_filename: str, melding: M, media_type: str, user: U) -> A: ...


class BaseAssetFactory[AS: Asset, AT: AssetType, M: Melding](metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, external_id: str, asset_type: AT, melding: M, label: str, subtype: str) -> AS: ...


class BaseNoteFactory[N: Note, M: Melding, U: User](metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, text: str, melding: M, user: U) -> N: ...
