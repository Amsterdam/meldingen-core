from typing import Generic, TypeVar

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
