from unittest.mock import AsyncMock, Mock

import pytest

from meldingen_core.actions.asset import ListAssetsAction, MelderListAssetsAction
from meldingen_core.managers import RelationshipManager
from meldingen_core.models import Asset, Melding
from meldingen_core.repositories import BaseMeldingRepository
from meldingen_core.token import TokenVerifier


class TestListAssetsAction:

    @pytest.mark.anyio
    async def test_can_list_assets(self) -> None:
        melding_id = 123

        melding: Melding = Melding(text="Test melding")
        melding_repository = Mock(BaseMeldingRepository)
        melding_repository.retrieve.return_value = melding
        relationship_manager = AsyncMock(RelationshipManager)

        action: ListAssetsAction[Asset, Melding] = ListAssetsAction(melding_repository, relationship_manager)
        await action(melding_id)

        melding_repository.retrieve.assert_awaited_once_with(melding_id)
        relationship_manager.get_related.assert_awaited_once_with(melding)

    @pytest.mark.anyio
    async def test_melder_can_list_assets(self) -> None:
        token = "supersecrettoken"
        melding_id = 123
        melding: Melding = Melding(text="Test melding")
        token_verifier = AsyncMock(TokenVerifier, return_value=melding)
        relationship_manager = AsyncMock(RelationshipManager)

        action: MelderListAssetsAction[Asset, Melding] = MelderListAssetsAction(token_verifier, relationship_manager)
        await action(melding_id, token)

        token_verifier.assert_awaited_once()
        relationship_manager.get_related.assert_awaited_once_with(melding)
