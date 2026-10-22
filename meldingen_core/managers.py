from collections.abc import Awaitable, Callable

from meldingen_core.repositories import BaseRepository


class RelationshipExistsException(Exception):
    """Raised when relationship already exists between parent and related model."""


class RelationshipManager[A, B]:
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
        """Add a relationship between model_a and model_b if it doesn't already exist."""
        related_items = await self._get_related(model_a)
        # Check if the model_b item already exists
        if model_b in related_items:
            raise RelationshipExistsException("The relationship already exists.")

        related_items.append(model_b)
        await self._repository.save(model_a)

        return model_a

    async def get_related(self, model_a: A) -> list[B]:
        """Get the related items for the given model_a."""
        return await self._get_related(model_a)

    async def set_related(self, model_a: A, related_items: list[B]) -> A:
        """Set the related items for the given model_a, replacing any existing relationships."""
        current_related = await self._get_related(model_a)
        current_related.clear()
        current_related.extend(related_items)
        await self._repository.save(model_a)

        return model_a
