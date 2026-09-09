from collections.abc import Sequence

from meldingen_core.managers import RelationshipManager
from meldingen_core.models import Asset, Melding
from meldingen_core.repositories import BaseMeldingRepository
from meldingen_core.repository_helpers import retrieve_or_raise_not_found


class ListAssetsAction[A: Asset, M: Melding]:
    _repository: BaseMeldingRepository[M]
    _relationship_manager: RelationshipManager[M, A]

    def __init__(self, repository: BaseMeldingRepository[M], relationship_manager: RelationshipManager[M, A]) -> None:
        self._repository = repository
        self._relationship_manager = relationship_manager

    async def __call__(self, melding_id: int) -> Sequence[A]:
        melding = await retrieve_or_raise_not_found(self._repository, melding_id)

        return await self._relationship_manager.get_related(melding)
