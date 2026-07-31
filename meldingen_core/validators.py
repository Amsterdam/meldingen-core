from abc import ABCMeta, abstractmethod

from meldingen_core.models import Melding


class MediaTypeNotAllowed(Exception): ...


class AttachmentLimitReached(Exception): ...


class BaseMediaTypeValidator(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, mime_type: str) -> None:
        """Checks if the provided MIME type is allowed, raises MediaTypeNotAllowed exception if not."""


class MediaTypeIntegrityError(Exception): ...


class BaseMediaTypeIntegrityValidator(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, media_type: str, data: bytes) -> None:
        """Checks if the provided media type matches the media type that is determined from the provided data,
        raises MediaTypeIntegrityError if not."""


class BaseAttachmentLimitValidator(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, melding: Melding) -> None:
        """Checks if the provided melding has reached the attachment limit, raises AttachmentLimitReached if so."""
