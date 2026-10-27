from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from meldingen_core.managers import RelationshipExistsException, RelationshipManager
from meldingen_core.repositories import BaseRepository


class DummyRelated:
    pass


class DummyModel:
    related: list[DummyRelated]

    def __init__(self) -> None:
        self.related = []


async def dummy_get_related(parent: DummyModel) -> list[DummyRelated]:
    return parent.related


class TestRelationshipManager:
    def test_can_instantiate_relationship_manager(self) -> None:
        repository = Mock()
        get_related = AsyncMock()
        manager: RelationshipManager[DummyModel, DummyRelated] = RelationshipManager(repository, get_related)

        assert isinstance(manager, RelationshipManager)
        assert manager._get_related == get_related
        assert manager._repository == repository

    @pytest.mark.anyio
    async def test_add_and_get_relationship(self) -> None:
        repository: BaseRepository[DummyModel] = MagicMock(BaseRepository)
        manager: RelationshipManager[DummyModel, DummyRelated] = RelationshipManager(repository, dummy_get_related)
        parent = DummyModel()
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

    @pytest.mark.anyio
    async def test_set_related(self) -> None:
        repository: BaseRepository[DummyModel] = MagicMock(BaseRepository)
        manager: RelationshipManager[DummyModel, DummyRelated] = RelationshipManager(repository, dummy_get_related)
        parent = DummyModel()
        related1 = DummyRelated()
        related2 = DummyRelated()

        await manager.set_related(parent, [related1, related2])
        assert parent.related == [related1, related2]

    @pytest.mark.anyio
    async def test_clear_related(self) -> None:
        repository: BaseRepository[DummyModel] = MagicMock(BaseRepository)
        manager: RelationshipManager[DummyModel, DummyRelated] = RelationshipManager(repository, dummy_get_related)
        parent = DummyModel()
        related = DummyRelated()

        await manager.add_relationship(parent, related)
        assert related in parent.related

        await manager.set_related(parent, [])
        assert related not in parent.related
        assert parent.related == []
