from typing import TypeVar

from meldingen_core.actions.base import BaseCRUDAction
from meldingen_core.models import AssetType
from meldingen_core.repositories import BaseRepository
from meldingen_core.wfs import WfsProviderFactory
from starlette.responses import StreamingResponse

AT = TypeVar("AT", bound=AssetType)

class AssetRetrieveAction(BaseCRUDAction[AT]):
    _wfs_provider_factory: WfsProviderFactory

    def __init__(self, wfs_provider_factory: WfsProviderFactory, repository: BaseRepository[AT]) -> None:
        self._wfs_provider_factor = wfs_provider_factory
        super().__init__(repository)


    async def __call__(
        self,
        slug: str,
        type_names: str,
        count: int = 1000,
        srs_name: str = "urn:ogc:def:crs:EPSG::4326",
        output_format: str = "application/json",
        filter: str | None = None,
    ) -> StreamingResponse:
        asset_type = self._repository.retrieve(slug)
        provider = self._wfs_provider_factory(asset_type)

        iterator, media_type = await provider(type_names, count, srs_name, output_format, filter)

        return StreamingResponse(iterator, media_type=media_type)

