from starlette.responses import StreamingResponse

from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import AssetType
from meldingen_core.repositories import BaseAssetTypeRepository
from meldingen_core.wfs import WfsProviderFactory


class AssetRetrieveAction:
    _wfs_provider_factory: WfsProviderFactory
    _asset_type_repository: BaseAssetTypeRepository[AssetType]

    def __init__(
        self,
        wfs_provider_factory: WfsProviderFactory,
        asset_type_repository: BaseAssetTypeRepository[AssetType]
    ) -> None:
        self._wfs_provider_factory = wfs_provider_factory
        self._asset_type_repository = asset_type_repository

    async def __call__(
        self,
        slug: str,
        type_names: str,
        count: int = 1000,
        srs_name: str = "urn:ogc:def:crs:EPSG::4326",
        output_format: str = "application/json",
        filter: str | None = None,
    ) -> StreamingResponse:
        asset_type = await self._asset_type_repository.find_by_name(slug)

        if asset_type is None:
            raise NotFoundException("AssetType not found")

        provider = self._wfs_provider_factory(asset_type)

        iterator, media_type = await provider(type_names, count, srs_name, output_format, filter)

        return StreamingResponse(iterator, media_type=media_type)
