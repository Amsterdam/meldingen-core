from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from meldingen_core.managers import RelationshipExistsException, RelationshipManager
from meldingen_core.repositories import BaseRepository


class DummyRelated:
    pass


class DummyParent:
    related: list[DummyRelated]

    def __init__(self) -> None:
        self.related = []


async def dummy_get_related(parent: DummyParent) -> list[DummyRelated]:
    return parent.related


class TestRelationshipManager:

    def test_can_instantiate_relationship_manager(self) -> None:
        repository = Mock()
        get_related = AsyncMock()
        manager = RelationshipManager(repository, get_related)

        assert isinstance(manager, RelationshipManager)
        assert manager._get_related == get_related
        assert manager._repository == repository

    @pytest.mark.anyio
    async def test_add_and_get_relationship(self) -> None:
        repository = MagicMock(BaseRepository)
        manager = RelationshipManager(repository, dummy_get_related)
        parent = DummyParent()
        related = DummyRelated()

        # Should add relationship
        await manager.add_relationship(parent, related)
        assert related in parent.related
        assert parent.related.count(related) == 1

        # Should retrieve related items
        result = await manager.get_related(parent)
        assert result == parent.related

        # Should not add again
        with pytest.raises(RelationshipExistsException):
            await manager.add_relationship(parent, related)

            assert related in parent.related
            assert parent.related.count(related) == 1
