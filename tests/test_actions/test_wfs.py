from unittest.mock import AsyncMock, Mock

import pytest

from meldingen_core.actions.wfs import WfsRetrieveAction
from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import AssetType
from meldingen_core.repositories import BaseAssetTypeRepository
from meldingen_core.wfs import BaseWfsProvider, WfsProviderFactory


class TestWfsAction:
    def test_can_instantiate_retrieve_action(self) -> None:
        action: WfsRetrieveAction[AssetType] = WfsRetrieveAction(
            Mock(WfsProviderFactory), Mock(BaseAssetTypeRepository)
        )
        assert isinstance(action, WfsRetrieveAction)

    @pytest.mark.anyio
    async def test_retrieve_action(self) -> None:
        asset_type_mock = Mock(AssetType)
        repository = AsyncMock(BaseAssetTypeRepository)
        repository.retrieve.return_value = asset_type_mock

        provider = AsyncMock(BaseWfsProvider)
        factory = Mock(WfsProviderFactory)
        factory.return_value = provider

        action: WfsRetrieveAction[AssetType] = WfsRetrieveAction(factory, repository)

        await action(asset_type_id=1, type_names="test")

        repository.retrieve.assert_awaited_once_with(1)
        factory.assert_called_once_with(asset_type_mock)
        provider.assert_awaited_once_with(
            "test",
            1000,
            "urn:ogc:def:crs:EPSG::4326",
            "application/json",
            "WFS",
            "2.0.0",
            "GetFeature",
            None,
        )

    @pytest.mark.anyio
    async def test_asset_type_not_found(self) -> None:
        factory = Mock(WfsProviderFactory)
        repository = Mock(BaseAssetTypeRepository)

        repository.retrieve = AsyncMock(return_value=None)

        action: WfsRetrieveAction[AssetType] = WfsRetrieveAction(factory, repository)

        with pytest.raises(NotFoundException) as exception_info:
            await action(asset_type_id=1, type_names="test")

        assert str(exception_info.value) == "AssetType not found"
