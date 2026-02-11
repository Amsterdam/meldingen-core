from unittest.mock import AsyncMock, Mock

import pytest

from meldingen_core.actions.asset_type import (
    AssetTypeCreateAction,
    AssetTypeDeleteAction,
    AssetTypeListAction,
    AssetTypeRetrieveAction,
    AssetTypeUpdateAction,
    ValidateAssetTypeWfsAction,
)
from meldingen_core.models import AssetType
from meldingen_core.repositories import BaseAssetTypeRepository
from meldingen_core.wfs import WfsProviderFactory


def test_can_instantiate_create_action() -> None:
    action: AssetTypeCreateAction[AssetType] = AssetTypeCreateAction(Mock(BaseAssetTypeRepository))
    assert isinstance(action, AssetTypeCreateAction)


def test_can_instantiate_retrieve_action() -> None:
    action: AssetTypeRetrieveAction[AssetType] = AssetTypeRetrieveAction(Mock(BaseAssetTypeRepository))
    assert isinstance(action, AssetTypeRetrieveAction)


def test_can_instantiate_list_action() -> None:
    action: AssetTypeListAction[AssetType] = AssetTypeListAction(Mock(BaseAssetTypeRepository))
    assert isinstance(action, AssetTypeListAction)


def test_can_instantiate_update_action() -> None:
    action: AssetTypeUpdateAction[AssetType] = AssetTypeUpdateAction(Mock(BaseAssetTypeRepository))
    assert isinstance(action, AssetTypeUpdateAction)


def test_can_instantiate_delete_action() -> None:
    action: AssetTypeDeleteAction[AssetType] = AssetTypeDeleteAction(Mock(BaseAssetTypeRepository))
    assert isinstance(action, AssetTypeDeleteAction)


def test_can_instantiate_validate_wfs_action() -> None:
    action: ValidateAssetTypeWfsAction[AssetType] = ValidateAssetTypeWfsAction(Mock(WfsProviderFactory))
    assert isinstance(action, ValidateAssetTypeWfsAction)


@pytest.mark.anyio
async def test_validate_wfs_action_calls_factory_validate() -> None:
    factory = Mock(WfsProviderFactory)
    factory.validate = AsyncMock()
    action: ValidateAssetTypeWfsAction[AssetType] = ValidateAssetTypeWfsAction(factory)
    asset_type = Mock(AssetType)

    await action(asset_type)

    factory.validate.assert_awaited_once_with(asset_type)
