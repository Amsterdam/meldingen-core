from unittest.mock import Mock

from meldingen_core.actions.asset_type import (
    AssetTypeCreateAction,
    AssetTypeDeleteAction,
    AssetTypeRetrieveAction,
    AssetTypeUpdateAction,
)
from meldingen_core.models import AssetType
from meldingen_core.repositories import BaseAssetTypeRepository


def test_can_instantiate_create_action() -> None:
    action: AssetTypeCreateAction[AssetType] = AssetTypeCreateAction(Mock(BaseAssetTypeRepository))
    assert isinstance(action, AssetTypeCreateAction)


def test_can_instantiate_retrieve_action() -> None:
    action: AssetTypeRetrieveAction[AssetType] = AssetTypeRetrieveAction(Mock(BaseAssetTypeRepository))
    assert isinstance(action, AssetTypeRetrieveAction)


def test_can_instantiate_update_action() -> None:
    action: AssetTypeUpdateAction[AssetType] = AssetTypeUpdateAction(Mock(BaseAssetTypeRepository))
    assert isinstance(action, AssetTypeUpdateAction)


def test_can_instantiate_delete_action() -> None:
    action: AssetTypeDeleteAction[AssetType] = AssetTypeDeleteAction(Mock(BaseAssetTypeRepository))
    assert isinstance(action, AssetTypeDeleteAction)
