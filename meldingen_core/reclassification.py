from abc import ABC, ABCMeta, abstractmethod
from typing import Generic, TypeVar

from meldingen_core.models import Asset, Classification, Melding
from meldingen_core.repositories import BaseAssetRepository, BaseMeldingRepository

M = TypeVar("M", bound=Melding)
AS = TypeVar("AS", bound=Asset)


class BaseReclassification(Generic[AS, M], metaclass=ABCMeta):
    _asset_repository: BaseAssetRepository[AS]
    _melding_repository: BaseMeldingRepository[M]

    def __init__(self, asset_repository: BaseAssetRepository[AS], melding_repository: BaseMeldingRepository[M]) -> None:
        self._asset_repository = asset_repository
        self._melding_repository = melding_repository

    @abstractmethod
    async def __call__(self, melding: Melding, new_classification: Classification | None) -> None:
        """Handle reclassification side effects here, like changing the assets or removing/changing the location."""
