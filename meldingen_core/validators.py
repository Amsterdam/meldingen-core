from abc import ABCMeta, abstractmethod
from typing import Any


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


class InvalidMeldingDataException(Exception): ...


class BaseMeldingUpdateValidator(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, values: dict[str, Any]) -> None:
        """Abstraction to check if data related to a Melding is valid, f.e. checks if given labels exist. Raises InvalidMeldingDataException if not.
        Can be used for additional checks in the implementation that can't be done in the core."""
