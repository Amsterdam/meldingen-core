from unittest.mock import Mock

from meldingen_core.actions.asset import AssetRetrieveAction
from meldingen_core.repositories import BaseAssetTypeRepository
from meldingen_core.wfs import WfsProviderFactory


def test_can_instantiate_retrieve_action() -> None:
    action: AssetRetrieveAction = AssetRetrieveAction(Mock(WfsProviderFactory), Mock(BaseAssetTypeRepository))
    assert isinstance(action, AssetRetrieveAction)