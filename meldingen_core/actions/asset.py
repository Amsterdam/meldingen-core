from typing import Generic, Sequence, TypeVar

from meldingen_core.managers import RelationshipManager
from meldingen_core.models import Asset, Melding
from meldingen_core.repositories import BaseMeldingRepository
from meldingen_core.token import TokenVerifier

A = TypeVar("A", bound=Asset)
M = TypeVar("M", bound=Melding)


class MelderListAssetsAction(Generic[A, M]):
    _verify_token: TokenVerifier[M]
    _relationship_manager: RelationshipManager[M, A]

    def __init__(self, token_verifier: TokenVerifier[M], relationship_manager: RelationshipManager[M, A]) -> None:
        self._verify_token = token_verifier
        self._relationship_manager = relationship_manager

    async def __call__(self, melding_id: int, token: str) -> Sequence[A]:
        melding = await self._verify_token(melding_id, token)

        return await self._relationship_manager.get_related(melding)


class ListAssetsAction(Generic[A, M]):
    _melding_repository: BaseMeldingRepository[M]
    _relationship_manager: RelationshipManager[M, A]

    def __init__(
        self, melding_repository: BaseMeldingRepository[M], relationship_manager: RelationshipManager[M, A]
    ) -> None:
        self._melding_repository = melding_repository
        self._relationship_manager = relationship_manager

    async def __call__(self, melding_id: int) -> Sequence[A]:
        melding = await self._melding_repository.retrieve(melding_id)
        assert melding is not None

        return await self._relationship_manager.get_related(melding)
