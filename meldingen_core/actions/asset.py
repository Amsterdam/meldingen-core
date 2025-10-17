from typing import Generic, Sequence, TypeVar

from meldingen_core.models import Asset, Melding
from meldingen_core.repositories import BaseAssetRepository
from meldingen_core.token import TokenVerifier

A = TypeVar("A", bound=Asset)
M = TypeVar("M", bound=Melding)


class MelderListAssetsAction(Generic[A, M]):
    _verify_token: TokenVerifier[M]
    _asset_repository: BaseAssetRepository[A]

    def __init__(self, token_verifier: TokenVerifier[M], asset_repository: BaseAssetRepository[A]):
        self._verify_token = token_verifier
        self._asset_repository = asset_repository

    async def __call__(self, melding_id: int, token: str) -> Sequence[A]:
        await self._verify_token(melding_id, token)

        return await self._asset_repository.find_by_melding(melding_id)


class ListAssetsAction(Generic[A]):
    _asset_repository: BaseAssetRepository[A]

    def __init__(self, asset_repository: BaseAssetRepository[A]):
        self._asset_repository = asset_repository

    async def __call__(self, melding_id: int) -> Sequence[A]:
        return await self._asset_repository.find_by_melding(melding_id)
