from typing import Generic, TypeVar

from meldingen_core.actions.base import (
    BaseCreateAction,
    BaseDeleteAction,
    BaseListAction,
    BaseRetrieveAction,
    BaseUpdateAction,
)
from meldingen_core.models import AssetType
from meldingen_core.wfs import WfsProviderFactory

AT = TypeVar("AT", bound=AssetType)


class AssetTypeCreateAction(BaseCreateAction[AT]): ...


class AssetTypeRetrieveAction(BaseRetrieveAction[AT]): ...


class AssetTypeListAction(BaseListAction[AT]): ...


class AssetTypeUpdateAction(BaseUpdateAction[AT]): ...


class AssetTypeDeleteAction(BaseDeleteAction[AT]): ...


class ValidateAssetTypeWfsAction(Generic[AT]):
    _wfs_provider_factory: WfsProviderFactory

    def __init__(self, wfs_provider_factory: WfsProviderFactory) -> None:
        self._wfs_provider_factory = wfs_provider_factory

    async def __call__(self, asset_type: AT) -> None:
        await self._wfs_provider_factory.validate(asset_type)
