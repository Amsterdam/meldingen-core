from abc import ABCMeta, abstractmethod

from meldingen_core.models import Label


class MediaTypeNotAllowed(Exception): ...


class BaseMediaTypeValidator(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, mime_type: str) -> None:
        """Checks if the provided MIME type is allowed, raises a MIMETypeNotAllowed exception if not."""


class MediaTypeIntegrityError(Exception): ...


class BaseMediaTypeIntegrityValidator(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, media_type: str, data: bytes) -> None:
        """Checks if the provided media type matches the media type that is determined from the provided data,
        raises MediaTypeIntegrityError if not."""


class BaseLabelValidator(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, label_ids: list[int]) -> list[Label]:
        """Abstraction to check if given label id's exist. Will return retrieved labels if they can all be found. Raises NotFoundException if not."""
