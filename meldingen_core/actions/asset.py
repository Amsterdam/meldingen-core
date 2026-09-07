from typing import Generic, Sequence, TypeVar

from meldingen_core.exceptions import NotFoundException
from meldingen_core.managers import RelationshipManager
from meldingen_core.models import Asset, Melding
from meldingen_core.repositories import BaseMeldingRepository
from meldingen_core.repository_item import retrieve_or_raise

A = TypeVar("A", bound=Asset)
M = TypeVar("M", bound=Melding)


class ListAssetsAction(Generic[A, M]):
    _melding_repository: BaseMeldingRepository[M]
    _relationship_manager: RelationshipManager[M, A]

    def __init__(
        self, melding_repository: BaseMeldingRepository[M], relationship_manager: RelationshipManager[M, A]
    ) -> None:
        self._melding_repository = melding_repository
        self._relationship_manager = relationship_manager

    async def __call__(self, melding_id: int) -> Sequence[A]:

        melding = await retrieve_or_raise(self._melding_repository, melding_id)

        return await self._relationship_manager.get_related(melding)
