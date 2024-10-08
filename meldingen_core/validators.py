from abc import ABCMeta, abstractmethod


class MediaTypeNotAllowed(Exception): ...


class BaseMediaTypeValidator(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, mime_type: str) -> None:
        """Checks if the provided MIME type is allowed, raises a MIMETypeNotAllowed exception if not."""
