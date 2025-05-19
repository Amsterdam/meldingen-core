from abc import ABCMeta, abstractmethod  # pragma: no cover


class BasePreviewMailAction(metaclass=ABCMeta):  # pragma: no cover
    @abstractmethod
    def __call__(self, title: str, preview_text: str, body_text: str) -> str: ...
