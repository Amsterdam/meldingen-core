from unittest.mock import AsyncMock, Mock

import pytest

from meldingen_core.actions.asset import ListAssetsAction, MelderListAssetsAction
from meldingen_core.models import Asset, Melding
from meldingen_core.repositories import BaseAssetRepository
from meldingen_core.token import TokenVerifier


class TestListAssetsAction:

    @pytest.mark.anyio
    async def test_can_list_assets(self) -> None:
        melding_id = 123
        repo_assets: list[Asset] = []
        repository = Mock(BaseAssetRepository)
        repository.find_by_melding.return_value = repo_assets

        action: ListAssetsAction[Asset] = ListAssetsAction(repository)
        assets = await action(melding_id)

        assert repo_assets == assets
        repository.find_by_melding.assert_awaited_once_with(melding_id)

    @pytest.mark.anyio
    async def test_melder_can_list_attachments(self) -> None:
        token = "supersecrettoken"
        melding_id = 123
        repo_assets: list[Asset] = []
        token_verifier = AsyncMock(TokenVerifier)
        repository = Mock(BaseAssetRepository)
        repository.find_by_melding.return_value = repo_assets

        action: MelderListAssetsAction[Asset, Melding] = MelderListAssetsAction(token_verifier, repository)
        assets = await action(melding_id, token)

        assert repo_assets == assets
        token_verifier.assert_awaited_once()
        repository.find_by_melding.assert_awaited_once_with(melding_id)
