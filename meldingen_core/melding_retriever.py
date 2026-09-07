from typing import Generic, TypeVar

from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository, BaseRepository

T = TypeVar("T", bound=Melding)


class MeldingRetriever(Generic[T]):
    _repository: BaseRepository[T]

    def __init__(self, repository: BaseRepository[T]):
        self._repository = repository

    async def __call__(self, pk: int) -> T:
        return await retrieve_or_raise(self._repository, pk)


async def retrieve_or_raise(repository: BaseRepository[T], pk: int, error_message: str = "Melding not found") -> T:
    item = await repository.retrieve(pk)
    if item is None:
        raise NotFoundException(error_message)

    return item
