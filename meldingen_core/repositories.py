from abc import ABCMeta, abstractmethod
from collections.abc import Collection, Sequence
from typing import Generic, TypeVar

from meldingen_core import SortingDirection
from meldingen_core.models import Answer, Attachment, Classification, Form, Melding, Question, User

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class BaseRepository(Generic[T, T_co], metaclass=ABCMeta):
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
    ) -> Collection[T_co]: ...

    @abstractmethod
    async def retrieve(self, pk: int) -> T | None: ...

    @abstractmethod
    async def delete(self, pk: int) -> None: ...


M = TypeVar("M", bound=Melding)
M_co = TypeVar("M_co", covariant=True, bound=Melding)


class BaseMeldingRepository(BaseRepository[M, M_co], metaclass=ABCMeta):
    """Repository for Melding."""


class BaseUserRepository(BaseRepository[User, User], metaclass=ABCMeta):
    """Repository for User."""


class BaseClassificationRepository(BaseRepository[Classification, Classification], metaclass=ABCMeta):
    """Repository for Classification."""

    @abstractmethod
    async def find_by_name(self, name: str) -> Classification:
        """Find a classification by name or raise NotFoundException if not found."""


class BaseFormRepository(BaseRepository[Form, Form], metaclass=ABCMeta): ...


class BaseQuestionRepository(BaseRepository[Question, Question], metaclass=ABCMeta): ...


class BaseAnswerRepository(BaseRepository[Answer, Answer], metaclass=ABCMeta):
    @abstractmethod
    async def find_by_melding(self, melding_id: int) -> Sequence[Answer]: ...


A = TypeVar("A", bound=Attachment)
A_co = TypeVar("A_co", covariant=True, bound=Attachment)


class BaseAttachmentRepository(BaseRepository[A, A_co], metaclass=ABCMeta):
    @abstractmethod
    async def find_by_melding(self, melding_id: int) -> Collection[A_co]: ...
