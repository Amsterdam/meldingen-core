from typing import AsyncIterator, Generic, Literal, TypeVar

from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import AssetType
from meldingen_core.repositories import BaseAssetTypeRepository
from meldingen_core.wfs import WfsProviderFactory

AT = TypeVar("AT", bound=AssetType)


class WfsRetrieveAction(Generic[AT]):
    _wfs_provider_factory: WfsProviderFactory
    _asset_type_repository: BaseAssetTypeRepository[AT]

    def __init__(
        self, wfs_provider_factory: WfsProviderFactory, asset_type_repository: BaseAssetTypeRepository[AT]
    ) -> None:
        self._wfs_provider_factory = wfs_provider_factory
        self._asset_type_repository = asset_type_repository

    async def __call__(
        self,
        name: str,
        type_names: str,
        count: int = 1000,
        srs_name: str = "urn:ogc:def:crs:EPSG::4326",
        output_format: Literal["application/json"] = "application/json",
        service: Literal["WFS"] = "WFS",
        version: str = "2.0.0",
        request: Literal["GetFeature"] = "GetFeature",
        filter: str | None = None,
    ) -> AsyncIterator[bytes]:
        asset_type = await self._asset_type_repository.find_by_name(name)

        if asset_type is None:
            raise NotFoundException("AssetType not found")

        provider = self._wfs_provider_factory(asset_type)

        return await provider(type_names, count, srs_name, output_format, service, version, request, filter)
