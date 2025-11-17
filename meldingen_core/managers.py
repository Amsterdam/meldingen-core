from typing import Awaitable, Callable, Generic, TypeVar

from meldingen_core.repositories import BaseRepository

A = TypeVar("A")  # Related model A
B = TypeVar("B")  # Related model B


class RelationshipExistsException(Exception):
    """Raised when relationship already exists between parent and related model."""

    pass


class RelationshipManager(Generic[A, B]):
    """Abstraction to manage relationships between models when there is no ORM implemented"""

    _repository: BaseRepository[A]
    _get_related: Callable[[A], Awaitable[list[B]]]  # Function to get related B items for a given A

    def __init__(
        self,
        repository: BaseRepository[A],
        get_related: Callable[[A], Awaitable[list[B]]],
    ) -> None:
        self._repository = repository
        self._get_related = get_related

    async def add_relationship(self, model_a: A, model_b: B) -> A:
        related_items = await self._get_related(model_a)

        # Check if the model_b item already exists
        if model_b in related_items:
            raise RelationshipExistsException("The relationship already exists.")

        related_items.append(model_b)
        await self._repository.save(model_a)

        return model_a

    async def get_related(self, model_a: A) -> list[B]:
        return await self._get_related(model_a)
