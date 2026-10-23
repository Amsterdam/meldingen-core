from abc import ABCMeta, abstractmethod
from collections.abc import Sequence

from meldingen_core import SortingDirection
from meldingen_core.filters import MeldingListFilters, NameListFilters
from meldingen_core.models import (
    Answer,
    Asset,
    AssetType,
    Attachment,
    Classification,
    Form,
    Label,
    Melding,
    Note,
    Question,
    Source,
    User,
)


class BaseRepository[T](metaclass=ABCMeta):
    @abstractmethod
    async def save(self, obj: T) -> None: ...

    @abstractmethod
    async def list(
        self,
        limit: int | None = None,
        offset: int | None = None,
        sort_attribute_name: str | None = None,
        sort_direction: SortingDirection | None = None,
        filters: NameListFilters | None = None,
        apply_visibility_filters: bool = True,
    ) -> Sequence[T]: ...

    @abstractmethod
    async def retrieve(self, pk: int) -> T | None: ...

    @abstractmethod
    async def delete(self, pk: int) -> None: ...


class BaseMeldingRepository[M: Melding](BaseRepository[M], metaclass=ABCMeta):
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


class BaseUserRepository[U: User](BaseRepository[U], metaclass=ABCMeta):
    """Repository for User."""


class BaseClassificationRepository[C: Classification](BaseRepository[C], metaclass=ABCMeta):
    """Repository for Classification."""

    @abstractmethod
    async def find_by_name(self, name: str) -> C:
        """Find a classification by name or raise NotFoundException if not found."""


class BaseFormRepository[F: Form](BaseRepository[F], metaclass=ABCMeta): ...


class BaseQuestionRepository[Q: Question](BaseRepository[Q], metaclass=ABCMeta): ...


class BaseAnswerRepository[A: Answer](BaseRepository[A], metaclass=ABCMeta):
    @abstractmethod
    async def find_by_melding(self, melding_id: int) -> Sequence[A]: ...

    @abstractmethod
    async def find_by_id_and_melding(self, answer_id: int, melding_id: int) -> A | None: ...


class BaseAttachmentRepository[AT: Attachment](BaseRepository[AT], metaclass=ABCMeta):
    @abstractmethod
    async def find_by_melding(self, melding_id: int) -> Sequence[AT]: ...


class BaseAssetTypeRepository[AT: AssetType](BaseRepository[AT], metaclass=ABCMeta):
    @abstractmethod
    async def find_by_name(self, name: str) -> AT | None: ...

    @abstractmethod
    async def find_by_melding(self, melding_id: int) -> AT | None: ...


class BaseAssetRepository[AS: Asset](BaseRepository[AS], metaclass=ABCMeta):
    @abstractmethod
    async def find_by_external_id_and_asset_type_id(self, external_id: str, asset_type_id: int) -> AS | None: ...


class BaseLabelRepository[L: Label](BaseRepository[L], metaclass=ABCMeta):
    @abstractmethod
    async def list_by_ids(self, ids: list[int]) -> Sequence[L]: ...


class BaseSourceRepository[S: Source](BaseRepository[S], metaclass=ABCMeta):
    """Repository for Source."""


class BaseNoteRepository[N: Note](BaseRepository[N], metaclass=ABCMeta):
    @abstractmethod
    async def find_by_melding(
        self,
        melding_id: int,
        *,
        sort_attribute_name: str | None = None,
        sort_direction: SortingDirection | None = None,
    ) -> Sequence[N]: ...

    @abstractmethod
    async def find_by_id_and_melding(self, note_id: int, melding_id: int) -> N | None: ...
