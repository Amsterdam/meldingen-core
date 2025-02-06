from abc import ABCMeta, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeVar

from meldingen_core import SortingDirection
from meldingen_core.models import Answer, Attachment, Classification, Form, Melding, Question, User

T = TypeVar("T")


class BaseRepository(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    async def save(self, obj: T) -> None: ...

    @abstractmethod
    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_attribute_name: str | None = None,
        sort_direction: SortingDirection | None = None,
    ) -> Sequence[T]: ...

    @abstractmethod
    async def retrieve(self, pk: int) -> T | None: ...

    @abstractmethod
    async def delete(self, pk: int) -> None: ...


M = TypeVar("M", bound=Melding)


class BaseMeldingRepository(BaseRepository[M], metaclass=ABCMeta):
    """Repository for Melding."""


class BaseUserRepository(BaseRepository[User], metaclass=ABCMeta):
    """Repository for User."""


class BaseClassificationRepository(BaseRepository[Classification], metaclass=ABCMeta):
    """Repository for Classification."""

    @abstractmethod
    async def find_by_name(self, name: str) -> Classification:
        """Find a classification by name or raise NotFoundException if not found."""


class BaseFormRepository(BaseRepository[Form], metaclass=ABCMeta): ...


class BaseQuestionRepository(BaseRepository[Question], metaclass=ABCMeta): ...


Ans = TypeVar("Ans", bound=Answer)


class BaseAnswerRepository(BaseRepository[Ans], metaclass=ABCMeta):
    @abstractmethod
    async def find_by_melding(self, melding_id: int) -> Sequence[Ans]: ...


A = TypeVar("A", bound=Attachment)


class BaseAttachmentRepository(BaseRepository[A], metaclass=ABCMeta):
    @abstractmethod
    async def find_by_melding(self, melding_id: int) -> Sequence[A]: ...
