from typing import Any

from meldingen_core.actions.base import (
    BaseCRUDAction,
    BaseDeleteAction,
    BaseListAction,
    BaseRetrieveAction,
)
from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import AssetType
from meldingen_core.repositories import BaseRepository
from meldingen_core.wfs import BaseWfsProviderValidator


class AssetTypeCreateAction[AT: AssetType](BaseCRUDAction[AT]):
    _wfs_provider_validator: BaseWfsProviderValidator

    def __init__(self, repository: BaseRepository[AT], wfs_provider_validator: BaseWfsProviderValidator) -> None:
        super().__init__(repository)
        self._wfs_provider_validator = wfs_provider_validator

    async def __call__(self, obj: AT) -> None:
        await self._wfs_provider_validator(obj)
        await self._repository.save(obj)


class AssetTypeRetrieveAction[AT: AssetType](BaseRetrieveAction[AT]): ...


class AssetTypeListAction[AT: AssetType](BaseListAction[AT]): ...


class AssetTypeUpdateAction[AT: AssetType](BaseCRUDAction[AT]):
    _wfs_provider_validator: BaseWfsProviderValidator

    def __init__(self, repository: BaseRepository[AT], wfs_provider_validator: BaseWfsProviderValidator) -> None:
        super().__init__(repository)
        self._wfs_provider_validator = wfs_provider_validator

    async def __call__(self, pk: int, values: dict[str, Any]) -> AT:
        obj = await self._repository.retrieve(pk=pk)
        if obj is None:
            raise NotFoundException()

        for key, value in values.items():
            setattr(obj, key, value)

        if "class_name" in values or "arguments" in values:
            await self._wfs_provider_validator(obj)

        await self._repository.save(obj)
        return obj


class AssetTypeDeleteAction[AT: AssetType](BaseDeleteAction[AT]): ...
