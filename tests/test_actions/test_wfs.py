from unittest.mock import AsyncMock, Mock

import pytest

from meldingen_core.actions.wfs import WfsRetrieveAction
from meldingen_core.exceptions import NotFoundException
from meldingen_core.repositories import BaseAssetTypeRepository
from meldingen_core.wfs import WfsProviderFactory


class TestWfsAction:
    def test_can_instantiate_retrieve_action(self) -> None:
        action: WfsRetrieveAction = WfsRetrieveAction(Mock(WfsProviderFactory), Mock(BaseAssetTypeRepository))
        assert isinstance(action, WfsRetrieveAction)

    @pytest.mark.anyio
    async def test_asset_type_not_found(self) -> None:
        factory = Mock(WfsProviderFactory)
        repository = Mock(BaseAssetTypeRepository)

        repository.find_by_name = AsyncMock(return_value=None)

        action: WfsRetrieveAction = WfsRetrieveAction(factory, repository)

        with pytest.raises(NotFoundException) as exception_info:
            await action(name="test", type_names="test")

        assert str(exception_info.value) == "AssetType not found"
