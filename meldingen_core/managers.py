from collections.abc import Awaitable, Callable

from meldingen_core.repositories import BaseRepository


class RelationshipExistsException(Exception):
    """Raised when relationship already exists between parent and related model."""


class RelationshipManager[A, B]:
    """Abstraction to manage relationships between models when there is no ORM implemented.
    It uses abstracted methods to get and save related items between models, because the ORM implementation can vary and may not provide built-in relationship management.

    The meldingen FastAPI implementation uses the cascade save-update strategy for managing relationships between models.
    This means that when a parent model is saved, any changes to its related models are also persisted automatically.
    Therefore only a model_a.save() would suffice.
    This may not be the case for other implementations, so for longevity we may need to rework this class to be more abstract and adaptable to different ORM strategies.
    """

    _repository: BaseRepository[A]
    _get_related: Callable[[A], Awaitable[list[B]]]  # Function to get related B items for a given A
    _save_related: Callable[
        [A, list[B]], Awaitable[None]
    ]  # Function to save related B items for a given A (can include updated fields of B aswell)

    def __init__(
        self,
        repository: BaseRepository[A],
        get_related: Callable[[A], Awaitable[list[B]]],
        save_related: Callable[[A, list[B]], Awaitable[None]],
    ) -> None:
        self._repository = repository
        self._get_related = get_related
        self._save_related = save_related

    async def add_relationship(self, model_a: A, model_b: B) -> A:
        """Add a relationship between model_a and model_b if it doesn't already exist."""
        related_items = await self._get_related(model_a)
        # Check if the model_b item already exists
        if model_b in related_items:
            raise RelationshipExistsException("The relationship already exists.")

        related_items.append(model_b)
        await self._repository.save(model_a)
        await self._save_related(model_a, related_items)

        return model_a

    async def get_related(self, model_a: A) -> list[B]:
        """Get the related items for the given model_a."""
        return await self._get_related(model_a)

    async def set_related(self, model_a: A, related_items: list[B]) -> A:
        """Set the related items for the given model_a, replacing any existing relationships."""
        current_related = await self._get_related(model_a)
        current_related.clear()
        current_related.extend(related_items)

        await self._save_related(model_a, related_items)

        return model_a
