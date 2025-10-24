from typing import Awaitable, Callable, Generic, TypeVar

from meldingen_core.repositories import BaseRepository

P = TypeVar("P")  # Parent model type
R = TypeVar("R")  # Related model type


class RelationshipExistsException(Exception):
    """Raised when relationship already exists between parent and related model."""

    pass


# Abstraction to manage relationships between models when there is no ORM implemented
class RelationshipManager(Generic[P, R]):
    _repository: BaseRepository[P]
    _get_related: Callable[[P], Awaitable[list[R]]]

    def __init__(
        self,
        repository: BaseRepository[P],
        get_related: Callable[[P], Awaitable[list[R]]],
    ) -> None:
        self._repository = repository
        self._get_related = get_related

    async def add_relationship(self, parent: P, related: R) -> P:
        related_items = await self._get_related(parent)

        # Check if the related item already exists
        if related in related_items:
            raise RelationshipExistsException("The relationship already exists.")

        related_items.append(related)
        await self._repository.save(parent)

        return parent

    async def get_related(self, parent: P) -> list[R]:
        return await self._get_related(parent)
