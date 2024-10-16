from abc import ABCMeta, abstractmethod


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
