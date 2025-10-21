from unittest.mock import AsyncMock, Mock

import pytest

from meldingen_core.managers import RelationshipManager


class DummyParent:
    pass


class DummyRelated:
    pass


@pytest.mark.asyncio
async def adds_relationship_when_not_existing() -> None:
    repository = Mock()
    repository.save = AsyncMock()
    get_related = AsyncMock(return_value=[])
    manager = RelationshipManager(repository, get_related)

    parent = DummyParent()
    related = DummyRelated()

    await manager.add_relationship(parent, related)

    get_related.assert_called_once_with(parent)
    repository.save.assert_awaited_once_with(parent)


@pytest.mark.asyncio
async def does_not_add_relationship_when_already_exists() -> None:
    repository = Mock()
    repository.save = AsyncMock()
    related_item = DummyRelated()
    get_related = AsyncMock(return_value=[related_item])
    manager = RelationshipManager(repository, get_related)

    parent = DummyParent()

    await manager.add_relationship(parent, related_item)

    get_related.assert_called_once_with(parent)
    repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def retrieves_related_items() -> None:
    related_items = [DummyRelated(), DummyRelated()]
    get_related = AsyncMock(return_value=related_items)
    repository = Mock()
    manager = RelationshipManager(repository, get_related)

    parent = DummyParent()

    result = await manager.get_related(parent)

    get_related.assert_called_once_with(parent)
    assert result == related_items
