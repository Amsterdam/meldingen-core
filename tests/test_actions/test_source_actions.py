from unittest.mock import Mock

import pytest

from meldingen_core.actions.source import SourceListAction
from meldingen_core.models import Source
from meldingen_core.repositories import BaseSourceRepository


def test_can_instantiate_source_list_action() -> None:
    action: SourceListAction[Source] = SourceListAction(Mock(BaseSourceRepository))
    assert isinstance(action, SourceListAction)


@pytest.mark.anyio
async def test_source_list_action() -> None:
    repository = Mock(BaseSourceRepository)
    action: SourceListAction[Source] = SourceListAction(repository)

    await action()

    repository.list.assert_awaited_once()
