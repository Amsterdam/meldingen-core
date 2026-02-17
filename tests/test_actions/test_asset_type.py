from unittest.mock import AsyncMock, Mock

import pytest

from meldingen_core.actions.asset_type import (
    AssetTypeCreateAction,
    AssetTypeDeleteAction,
    AssetTypeListAction,
    AssetTypeRetrieveAction,
    AssetTypeUpdateAction,
)
from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import AssetType
from meldingen_core.repositories import BaseAssetTypeRepository
from meldingen_core.wfs import BaseWfsProviderValidator


def test_can_instantiate_create_action() -> None:
    action: AssetTypeCreateAction[AssetType] = AssetTypeCreateAction(
        Mock(BaseAssetTypeRepository), Mock(BaseWfsProviderValidator)
    )
    assert isinstance(action, AssetTypeCreateAction)


def test_can_instantiate_retrieve_action() -> None:
    action: AssetTypeRetrieveAction[AssetType] = AssetTypeRetrieveAction(Mock(BaseAssetTypeRepository))
    assert isinstance(action, AssetTypeRetrieveAction)


def test_can_instantiate_list_action() -> None:
    action: AssetTypeListAction[AssetType] = AssetTypeListAction(Mock(BaseAssetTypeRepository))
    assert isinstance(action, AssetTypeListAction)


def test_can_instantiate_update_action() -> None:
    action: AssetTypeUpdateAction[AssetType] = AssetTypeUpdateAction(
        Mock(BaseAssetTypeRepository), Mock(BaseWfsProviderValidator)
    )
    assert isinstance(action, AssetTypeUpdateAction)


def test_can_instantiate_delete_action() -> None:
    action: AssetTypeDeleteAction[AssetType] = AssetTypeDeleteAction(Mock(BaseAssetTypeRepository))
    assert isinstance(action, AssetTypeDeleteAction)


@pytest.mark.anyio
async def test_create_action_calls_validator_then_saves() -> None:
    repository = Mock(BaseAssetTypeRepository)
    repository.save = AsyncMock()
    validator = AsyncMock(BaseWfsProviderValidator)
    action: AssetTypeCreateAction[AssetType] = AssetTypeCreateAction(repository, validator)
    asset_type = Mock(AssetType)

    await action(asset_type)

    validator.assert_awaited_once_with(asset_type)
    repository.save.assert_awaited_once_with(asset_type)


@pytest.mark.anyio
async def test_update_action_calls_validator_when_class_name_changes() -> None:
    asset_type = Mock(AssetType)
    repository = Mock(BaseAssetTypeRepository)
    repository.retrieve = AsyncMock(return_value=asset_type)
    repository.save = AsyncMock()
    validator = AsyncMock(BaseWfsProviderValidator)
    action: AssetTypeUpdateAction[AssetType] = AssetTypeUpdateAction(repository, validator)

    await action(1, {"class_name": "new.ClassName"})

    validator.assert_awaited_once_with(asset_type)
    repository.save.assert_awaited_once_with(asset_type)


@pytest.mark.anyio
async def test_update_action_calls_validator_when_arguments_change() -> None:
    asset_type = Mock(AssetType)
    repository = Mock(BaseAssetTypeRepository)
    repository.retrieve = AsyncMock(return_value=asset_type)
    repository.save = AsyncMock()
    validator = AsyncMock(BaseWfsProviderValidator)
    action: AssetTypeUpdateAction[AssetType] = AssetTypeUpdateAction(repository, validator)

    await action(1, {"arguments": {"base_url": "http://example.com"}})

    validator.assert_awaited_once_with(asset_type)
    repository.save.assert_awaited_once_with(asset_type)


@pytest.mark.anyio
async def test_update_action_skips_validation_when_no_wfs_fields_change() -> None:
    asset_type = Mock(AssetType)
    repository = Mock(BaseAssetTypeRepository)
    repository.retrieve = AsyncMock(return_value=asset_type)
    repository.save = AsyncMock()
    validator = AsyncMock(BaseWfsProviderValidator)
    action: AssetTypeUpdateAction[AssetType] = AssetTypeUpdateAction(repository, validator)

    await action(1, {"name": "new_name"})

    validator.assert_not_awaited()
    repository.save.assert_awaited_once_with(asset_type)


@pytest.mark.anyio
async def test_update_action_raises_not_found() -> None:
    repository = Mock(BaseAssetTypeRepository)
    repository.retrieve = AsyncMock(return_value=None)
    validator = AsyncMock(BaseWfsProviderValidator)
    action: AssetTypeUpdateAction[AssetType] = AssetTypeUpdateAction(repository, validator)

    with pytest.raises(NotFoundException):
        await action(1, {"name": "new_name"})
