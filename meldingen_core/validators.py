from abc import ABCMeta, abstractmethod


class MIMETypeNotAllowed(Exception): ...


class BaseMIMETypeValidator(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, mime_type: str) -> None:
        """Checks if the provided MIME type is allowed, raises a MIMETypeNotAllowed exception if not."""
