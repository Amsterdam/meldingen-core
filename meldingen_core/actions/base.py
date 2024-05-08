from collections.abc import Collection
from typing import Any, Generic, TypeVar

from meldingen_core import SortingDirection
from meldingen_core.exceptions import NotFoundException
from meldingen_core.repositories import BaseRepository

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class BaseCRUDAction(Generic[T, T_co]):
    _repository: BaseRepository[T, T_co]

    def __init__(self, repository: BaseRepository[T, T_co]) -> None:
        self._repository = repository


class BaseCreateAction(BaseCRUDAction[T, T_co]):
    async def __call__(self, obj: T) -> None:
        await self._repository.save(obj)


class BaseRetrieveAction(BaseCRUDAction[T, T_co]):
    async def __call__(self, pk: int) -> T | None:
        return await self._repository.retrieve(pk=pk)


class BaseListAction(BaseCRUDAction[T, T_co]):
    async def __call__(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_attribute_name: str | None = None,
        sort_direction: SortingDirection | None = None,
    ) -> Collection[T_co]:
        return await self._repository.list(
            limit=limit, offset=offset, sort_attribute_name=sort_attribute_name, sort_direction=sort_direction
        )


class BaseUpdateAction(BaseCRUDAction[T, T_co]):
    async def __call__(self, pk: int, values: dict[str, Any]) -> T:
        obj = await self._repository.retrieve(pk=pk)
        if obj is None:
            raise NotFoundException()

        for key, value in values.items():
            setattr(obj, key, value)

        await self._repository.save(obj)

        return obj


class BaseDeleteAction(BaseCRUDAction[T, T_co]):
    async def __call__(self, pk: int) -> None:
        await self._repository.delete(pk=pk)
