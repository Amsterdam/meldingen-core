from abc import ABCMeta, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeVar

from meldingen_core import SortingDirection
from meldingen_core.filters import MeldingListFilters
from meldingen_core.models import Answer, Asset, AssetType, Attachment, Classification, Form, Melding, Question, User

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
    @abstractmethod
    async def list_meldingen(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_attribute_name: str | None = None,
        sort_direction: SortingDirection | None = None,
        filters: MeldingListFilters | None = None,
    ) -> Sequence[M]: ...


class BaseUserRepository(BaseRepository[User], metaclass=ABCMeta):
    """Repository for User."""


C = TypeVar("C", bound=Classification)


class BaseClassificationRepository(BaseRepository[C], metaclass=ABCMeta):
    """Repository for Classification."""

    @abstractmethod
    async def find_by_name(self, name: str) -> C:
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


AT = TypeVar("AT", bound=AssetType)


class BaseAssetTypeRepository(BaseRepository[AT], metaclass=ABCMeta):
    @abstractmethod
    async def find_by_name(self, name: str) -> AT | None: ...


AS = TypeVar("AS", bound=Asset)


class BaseAssetRepository(BaseRepository[AS], metaclass=ABCMeta):
    @abstractmethod
    async def find_by_external_id_and_asset_type_id(self, external_id: str, asset_type_id: int) -> AS | None: ...
